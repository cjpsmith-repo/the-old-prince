# Usage: ruby extract2.rb GAMES.json OUT.jsonl SHARD NSHARDS
# For each split: re-optimises the parent's routes at its next runs, with and
# without the stations it handed to the branch. Also logs train sales between
# companies.
ENV['ENGINE_LOG_LEVEL'] = '4'
require 'json'
require 'require_all'
LIB = File.expand_path(ENV.fetch('ENGINE_LIB', File.join(__dir__, 'eng', 'lib')))
require File.join(LIB, 'engine/logger')
require File.join(LIB, 'engine/debug')
require File.join(LIB, 'engine/deep_freeze')
require File.join(LIB, 'engine/game/base')
require File.join(LIB, 'engine/game/g_1871')
require_all File.join(LIB, 'engine/game/g_1871')
require File.join(LIB, 'engine/auto_router')

MAX_EVALS = (ENV['MAX_EVALS'] || 3).to_i

module Opt
  def self.overlap?(a, b)
    n = [a.size, b.size].min
    i = 0
    while i < n
      return true if (a[i] & b[i]) != 0
      i += 1
    end
    false
  end

  def self.merge(a, b)
    out = Array.new([a.size, b.size].max, 0)
    out.each_index { |i| out[i] = (a[i] || 0) | (b[i] || 0) }
    out
  end

  # best total revenue picking at most one route per train with disjoint track
  def self.best(game, corp)
    game.clear_graph_for_entity(corp)
    trains = game.route_trains(corp).sort_by(&:price)
    return [0, false] if trains.empty?
    ar = Engine::AutoRouter.new(game)
    tr, timed_out = ar.path(trains, corp, path_timeout: 25, route_limit: 400)
    lists = trains.map { |t| (tr[t] || []).map { |r| [r.revenue, r.bitfield] } }
    maxes = lists.map { |l| l.empty? ? 0 : l.first[0] }
    suffix = Array.new(lists.size + 1, 0)
    (lists.size - 1).downto(0) { |i| suffix[i] = suffix[i + 1] + maxes[i] }
    best = 0
    nodes = 0
    dfs = lambda do |i, bits, total|
      nodes += 1
      return if nodes > 2_000_000
      best = total if total > best
      return if i >= lists.size || total + suffix[i] <= best
      lists[i].each do |rev, bf|
        break if total + rev + suffix[i + 1] <= best
        next if overlap?(bits, bf)
        dfs.call(i + 1, merge(bits, bf), total + rev)
      end
      dfs.call(i + 1, bits, total)
    end
    dfs.call(0, [0], 0)
    [best, timed_out || nodes > 2_000_000]
  end
end

module Rec
  class << self; attr_accessor :out, :gid, :pending, :tracked; end
  def self.emit(h) = out.puts(JSON.generate(h.merge(gid: gid)))
end

module Hook2
  def process_single_action(action)
    r = round
    is_sr = r.is_a?(Engine::Game::G1871::Round::Stock)
    if is_sr && action.type == 'split' && action.entity.is_a?(Engine::Player)
      c = action.corporation
      Rec.pending = { parent: c.id, before_hexes: c.placed_tokens.map { |t| t.city&.hex&.id }, turn: turn, phase: phase.name }
    end
    if action.type == 'buy_train' && action.train.owner.is_a?(Engine::Corporation) && action.train.owner != action.entity
      seller = action.train.owner
      Rec.emit(t: 'tsale', turn: turn, phase: phase.name, buyer: action.entity.id, seller: seller.id, train: action.train.name,
               price: action.price, buyer_owner: action.entity.owner&.id.to_s, seller_owner: seller.owner&.id.to_s,
               buyer_cash: action.entity.cash, seller_cash: seller.cash,
               buyer_branch: action.entity.full_name.include?('Branch'), seller_branch: seller.full_name.include?('Branch'))
    end
    if action.type == 'run_routes'
      ent = action.entity
      (Rec.tracked || []).each do |sp|
        next unless sp[:parent] == ent.id && sp[:evals] < MAX_EVALS
        sp[:evals] += 1
        branch = corporation_by_id(sp[:branch])
        moved = branch.tokens.select { |t| t.used && t.city && sp[:moved_hexes].include?(t.city.hex.id) }
        blocked = moved.map { |t| t.city.blocks?(ent) }
        t0 = Time.now
        saved_branch = saved_parent = nil
        begin
        actual, to1 = Opt.best(self, ent)
        saved_branch = branch.tokens.dup
        saved_parent = ent.tokens.dup
        moved.each do |t|
          t.corporation = ent
          branch.tokens.delete(t)
          ent.tokens << t
        end
        cf, to2 = Opt.best(self, ent)
        moved.each { |t| t.corporation = branch }
        branch.tokens.replace(saved_branch)
        ent.tokens.replace(saved_parent)
        rescue StandardError => e
          moved.each { |t| t.corporation = branch }
          branch.tokens.replace(saved_branch) if saved_branch
          ent.tokens.replace(saved_parent) if saved_parent
          actual = cf = nil
          to1 = "#{e.class}: #{e.message[0, 80]}"
        end
        clear_graph_for_entity(ent)
        clear_graph_for_entity(branch)
        sp_ran = action.routes.sum { |rt| (rt.revenue rescue 0) }
        Rec.emit(t: 'cf', parent: ent.id, branch: sp[:branch], split_turn: sp[:turn], split_phase: sp[:phase], eval: sp[:evals],
                 turn: turn, rn: r.round_num, phase: phase.name, trains: ent.trains.map(&:name), ran: sp_ran,
                 opt_actual: actual, opt_cf: cf, timed_out: to1 || to2, moved: moved.size, blocked: blocked,
                 secs: (Time.now - t0).round(2))
      end
    end
    res = super
    if Rec.pending && is_sr && !round.split_active? && round.is_a?(Engine::Game::G1871::Round::Stock) && round.split_branch
      parent = corporation_by_id(Rec.pending[:parent])
      after = parent.placed_tokens.map { |t| t.city&.hex&.id }
      sp = Rec.pending.merge(branch: round.split_branch.id, moved_hexes: Rec.pending[:before_hexes] - after, evals: 0)
      Rec.tracked << sp
      Rec.emit(t: 'split2', parent: sp[:parent], branch: sp[:branch], moved_hexes: sp[:moved_hexes], turn: sp[:turn])
      Rec.pending = nil
    end
    res
  end
end
# Upstream hex_route_distance passes (conn, train) to a one-argument method.
module HexEdgeFix
  def hex_edge_cost(conn, _train = nil)
    conn[:paths].each_cons(2).sum { |a, b| a.hex == b.hex ? 0 : 1 }
  end
end
Engine::Game::G1871::Game.prepend(HexEdgeFix)
Engine::Game::G1871::Game.prepend(Hook2)

data = JSON.parse(File.read(ARGV[0]))
shard, nshard = ARGV[2].to_i, ARGV[3].to_i
File.open(ARGV[1], 'w') do |f|
  Rec.out = f
  f.sync = true
  data.each_with_index do |gd, i|
    next unless i % nshard == shard
    next unless gd['status'] == 'finished'
    next unless gd['actions'].any? { |a| a['type'] == 'split' }
    Rec.gid = gd['id']; Rec.pending = nil; Rec.tracked = []
    begin
      names = gd['players'].to_h { |p| [p['id'], p['name']] }
      game = Engine::Game::G1871::Game.new(names, id: gd['id'], actions: gd['actions'], seed: gd['settings']['seed'],
                                           optional_rules: gd['settings']['optional_rules'] || [])
      Rec.emit(t: "end2", bt: game.exception&.backtrace&.first(6), exception: game.exception&.message, match: game.result.transform_keys(&:to_s) == gd['result'])
    rescue StandardError => e
      Rec.emit(t: 'end2', exception: "#{e.class}: #{e.message[0, 200]}", fatal: true)
    end
  end
end
