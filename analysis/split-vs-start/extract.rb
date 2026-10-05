# Usage: ruby extract.rb GAMES.json OUT.jsonl SHARD NSHARDS
# Replays 1871 games with the 18xx.games engine and writes JSONL records.
ENV['ENGINE_LOG_LEVEL'] = '4'
require 'json'
require 'require_all'
# ENGINE_LIB points at the lib/ folder of a checkout of github.com/tobymao/18xx
LIB = File.expand_path(ENV.fetch('ENGINE_LIB', File.join(__dir__, 'eng', 'lib')))
require File.join(LIB, 'engine/logger')
require File.join(LIB, 'engine/debug')
require File.join(LIB, 'engine/deep_freeze')
require File.join(LIB, 'engine/game/base')
require File.join(LIB, 'engine/game/g_1871')
require_all File.join(LIB, 'engine/game/g_1871')

module Rec
  class << self; attr_accessor :out, :gid, :split; end
  def self.emit(h) = out.puts(JSON.generate(h.merge(gid: gid)))
end

module Snap
  def self.corp(g, c)
    holders = {}
    c.share_holders.each { |sh, pct| next if pct.zero?; holders[sh.respond_to?(:id) && sh.is_a?(Engine::Player) ? sh.id.to_s : (sh == g.share_pool ? 'pool' : sh.id.to_s)] = pct }
    {
      id: c.id, price: c.share_price&.price, cash: c.cash, trains: c.trains.map(&:name),
      tokens: c.placed_tokens.size, token_hexes: c.placed_tokens.map { |t| t.city&.hex&.id },
      floated: c.floated?, operated: c.operating_history.size, owner: c.owner&.id&.to_s,
      ml: g.mainline == c, sl: g.shortline == c, branch: c.full_name.include?('Branch'),
      holders: holders, cap: c.capitalization.to_s,
      treasury_buyable: c.shares_of(c).count(&:buyable), closed: c.closed?
    }
  end

  def self.players(g)
    g.players.reject { |p| p == g.union_bank }.map do |p|
      { id: p.id.to_s, cash: p.cash, value: g.player_value(p),
        hold: g.corporations.to_h { |c| [c.id, p.percent_of(c)] }.reject { |_, v| v.zero? },
        companies: p.companies.map(&:id) }
    end
  end
end

module Hook
  def process_single_action(action)
    g = self
    r = round
    is_sr = r.is_a?(Engine::Game::G1871::Round::Stock)
    ent = action.entity
    if is_sr && ent.is_a?(Engine::Player) && %w[buy_shares par split pass sell_shares].include?(action.type) && !r.split_active?
      splittable = corporations.select { |c| (can_split?(c, ent) rescue false) }.map { |c| Snap.corp(g, c).merge(my_pct: ent.percent_of(c)) }
      parable = corporations.select { |c| (can_par?(c, ent) rescue false) }.map(&:id)
      ppos = Snap.players(g)
      Rec.emit(t: 'sr', aid: action.id, turn: turn, phase: phase.name, pid: ent.id.to_s, cur: r.current_entity&.id.to_s,
               type: action.type, corp: (action.respond_to?(:corporation) ? action.corporation&.id : nil) ||
                                       (action.respond_to?(:bundle) ? action.bundle&.corporation&.id : nil),
               price: (action.respond_to?(:share_price) ? action.share_price&.price : nil),
               tranch: tranch_available?, tranche_idx: current_tranch_index, splittable: splittable, parable: parable,
               players: ppos, ub_owner: company_by_id('UB')&.owner&.id&.to_s)
      if action.type == 'split'
        c = action.corporation
        Rec.split = { parent_before: Snap.corp(g, c), turn: turn, phase: phase.name, pid: ent.id.to_s, aid: action.id,
                      players_before: ppos, moves: [] }
      end
    end
    if is_sr && r.split_active? && action.type == 'choose' && Rec.split
      Rec.split[:moves] << { step: r.instance_variable_get(:@split), choice: action.choice }
    end
    prev_round = r
    res = super
    if Rec.split && is_sr && !round.split_active? && Rec.split[:moves].any?
      sp = Rec.split
      parent = corporation_by_id(sp[:parent_before][:id])
      branch = round.is_a?(Engine::Game::G1871::Round::Stock) ? round.split_branch : nil
      Rec.emit(t: 'split', **sp, parent_after: Snap.corp(g, parent), branch_after: branch && Snap.corp(g, branch),
               players_after: Snap.players(g))
      Rec.split = nil
    end
    if round != prev_round
      Rec.emit(t: 'round', kind: round.class.name.split('::').last, turn: turn, rn: round.round_num, phase: phase.name,
               aid: action.id, corps: corporations.select { |c| c.ipoed || c.floated? }.map { |c| Snap.corp(g, c) },
               players: Snap.players(g), tranches: tranches.map { |tr| tr.map { |c| c&.id } })
    end
    res
  end
end
Engine::Game::G1871::Game.prepend(Hook)

data = JSON.parse(File.read(ARGV[0]))
shard, nshard = ARGV[2].to_i, ARGV[3].to_i
File.open(ARGV[1], 'w') do |f|
  Rec.out = f
  data.each_with_index do |gd, i|
    next unless i % nshard == shard
    Rec.gid = gd['id']; Rec.split = nil
    begin
      names = gd['players'].to_h { |p| [p['id'], p['name']] }
      game = Engine::Game::G1871::Game.new(names, id: gd['id'], actions: gd['actions'], seed: gd['settings']['seed'],
                                           optional_rules: gd['settings']['optional_rules'] || [])
      exc = game.exception&.message
      hist = game.corporations.to_h do |c|
        [c.id, c.operating_history.map { |(t, rn), oi| [t, rn, oi.revenue, oi.dividend&.kind] }]
      end
      Rec.emit(t: 'end', status: gd['status'], nplayers: gd['players'].size, exception: exc,
               recorded: gd['result'], engine_result: game.result.transform_keys(&:to_s), finished: game.finished,
               turn: game.turn, phase: game.phase.name, corps: game.corporations.map { |c| Snap.corp(game, c) },
               players: Snap.players(game), hist: hist, tranches: game.tranches.map { |tr| tr.map { |c| c&.id } },
               created_at: gd['created_at'], ml: game.mainline.id, sl: game.shortline.id,
               names: gd['players'].to_h { |p| [p['id'].to_s, p['name']] })
    rescue StandardError => e
      Rec.emit(t: 'end', status: gd['status'], exception: "#{e.class}: #{e.message[0, 200]}", fatal: true)
    end
  end
end
