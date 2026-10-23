"""Prop moves for story generators: show a map / page to chat, then put it in his back pocket (and take it out again).

Bible rule (user, 2026-10-23): Grandpa never walks or works with the map in his hand -- he needs his hands free.
He holds it up, the viewers see it big (a "page" card), he folds it and tucks it in his back pocket, and it pops into
the inventory hotbar (Minecraft-style). When he needs it again he takes it out of the pocket.

    acts, cards, item = show_and_pocket("map", t_pick=4.0, at_from=[0.3, -0.2, 0.76], t_pocket=7.5,
                                        page=dict(title="Grandpa's Map", map=...), icon="map", name="Map")
    acts2, t_out = take_out("map", t=20.0)
"""

STRAP = [-0.09, -0.17, 1.12]         # the webcam clipped to his right overall strap, lens forward (hands free)
POCKET_R = [-0.10, 0.13, 0.50]       # right back pocket, his own space (+y = behind him), origin between his feet
POCKET_L = [0.10, 0.13, 0.50]
SHOW_R = [-0.10, -0.36, 0.86]        # held out in front of his chest (below his face), toward whoever he faces
SHOW_L = [0.10, -0.36, 0.86]
FOLD_AT = 0.4                        # seconds to fold
TUCK = 0.5                           # seconds from folded to in the pocket


def show_and_pocket(target, t_pick, at_from, t_pocket, hand="R", grip=(0.0, 0.0, 0.0), rot_from=(0, 0, 0),
                    show_rot=(90, 0, 0), pocket_rot=(90, 0, 90), fold=0.35, page=None, icon="map", name=None,
                    reach=0.35, sound=True):
    """He picks the prop up from `at_from` (world) at t_pick, holds it up to show it (t_pick + 0.6 .. t_pocket), folds
    it and tucks it in his back pocket, where it rides along with him. Returns (actions, cards, inventory item)."""
    show = SHOW_R if hand == "R" else SHOW_L
    pocket = POCKET_R if hand == "R" else POCKET_L
    t_show = round(t_pick + 0.6, 3)
    t_fold = round(t_pocket + FOLD_AT, 3)
    t_in = round(t_fold + TUCK, 3)
    keys = [dict(t=round(t_pick, 3), at=at_from if isinstance(at_from, dict) else list(at_from), rot=list(rot_from), scale=1.0),
            dict(t=t_show, at={"char": show}, rot=list(show_rot), scale=1.0),
            dict(t=round(t_pocket, 3), at={"char": show}, rot=list(show_rot), scale=1.0),
            dict(t=t_fold, at={"char": [show[0], show[1] + 0.1, 0.85]}, rot=list(pocket_rot), scale=fold),
            dict(t=t_in, at={"char": pocket}, rot=list(pocket_rot), scale=fold)]
    acts = [dict(type="hold", target=target, hand=hand, when=round(t_pick, 3), until=t_in, reach=reach,
                 grip=list(grip), pocket=True, keys=keys)]
    if sound:
        acts += [dict(type="sfx", sound="page", when=round(t_pick, 3), gain=0.5),
                 dict(type="sfx", sound="page", when=round(t_pocket + 0.1, 3), gain=0.6)]
    cards = []
    if page is not None:
        cards.append(dict(page, style="page", when=round(t_show + 0.1, 3), until=round(t_pocket + 0.1, 3)))
    item = dict(icon=icon, name=name or target.replace("_", " ").title(), **{"in": t_in})
    return acts, cards, item


def take_out(target, t, hand="R", grip=(0.0, 0.0, 0.0), to=None, to_rot=(90, 0, 0), pocket_rot=(90, 0, 90), fold=0.35,
             reach=0.35, until=None, sound=True):
    """He reaches back and takes the prop out of his pocket at t, unfolding it on the way up to `to` (default: held up
    to show). Returns (actions, the time it leaves the inventory -- the item's "out")."""
    pocket = POCKET_R if hand == "R" else POCKET_L
    to = to or {"char": SHOW_R if hand == "R" else SHOW_L}
    keys = [dict(t=round(t, 3), at={"char": pocket}, rot=list(pocket_rot), scale=fold),
            dict(t=round(t + TUCK, 3), at={"char": [pocket[0], pocket[1] - 0.25, 0.85]}, rot=list(pocket_rot), scale=fold),
            dict(t=round(t + TUCK + FOLD_AT, 3), at=to, rot=list(to_rot), scale=1.0)]
    acts = [dict(type="hold", target=target, hand=hand, when=round(t, 3), until=round(until if until is not None else t + 99.0, 3),
                 reach=reach, grip=list(grip), keys=keys)]
    if sound:
        acts.append(dict(type="sfx", sound="page", when=round(t + TUCK, 3), gain=0.6))
    return acts, round(t, 3)


def clip_webcam(t, at_from, t_end, rot_from=(0, 0, 0), strap_rot=(0, 0, 0), hand="R", grip=(0.0, 0.0, 0.0), reach=0.35,
                cap=None):
    """Bible Rule 2 (revised 2026-10-23): travelling, the stream webcam rides clipped to his overall strap -- both hands
    free -- and the hotbar's first slot shows it LIVE. He takes it from `at_from` at t and clips it on (0.6 s); it rides
    along until t_end. `cap` = the lens-cap structure's name, if the webcam has one, to move with it.
    Returns (actions, the inventory item for the webcam)."""
    acts = []
    for name in [n for n in ("webcam", cap) if n]:
        acts.append(dict(type="hold", target=name, hand=hand if name == "webcam" else "none", when=round(t, 3),
                         until=round(t + 0.6, 3), reach=reach, grip=list(grip),
                         keys=[dict(t=round(t, 3), at=at_from if isinstance(at_from, dict) else list(at_from), rot=list(rot_from)),
                               dict(t=round(t + 0.6, 3), at={"char": STRAP}, rot=list(strap_rot)),
                               dict(t=round(t_end, 3), at={"char": STRAP}, rot=list(strap_rot))]))
    acts.append(dict(type="sfx", sound="switch", when=round(t + 0.6, 3), gain=0.4))
    return acts, dict(icon="webcam", name="Webcam", live=True, **{"in": -1.0})
