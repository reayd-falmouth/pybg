
def format_move(move):
    src = "bar" if move.source == -1 else str(move.source + 1)
    dst = "off" if move.destination == -1 else str(move.destination + 1)
    return f"{src}/{dst}"

def print_eval_results(results):
    for idx, (play, avg_eval, equity) in enumerate(results, start=1):
        moves_str = " ".join(format_move(m) for m in play.moves)
        print(f"{idx:2d}. Cubeful 2-ply    {moves_str:<20} Eq.: {equity:+.3f}")
        print(
            f"    {avg_eval['win_prob']:.3f} {avg_eval['gammon_prob']:.3f} 0.000 - {1 - avg_eval['win_prob']:.3f} {avg_eval['lose_gammon_prob']:.3f} 0.000"
        )
        print(f"     2-ply cubeful prune [world class]")