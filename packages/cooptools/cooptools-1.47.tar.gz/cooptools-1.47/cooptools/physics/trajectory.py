import logging
import math
import time

from cooptools.geometry_utils import vector_utils as vec
from cooptools.geometry_utils import circle_utils as circ
from cooptools.geometry_utils import line_utils as lin
import matplotlib.pyplot as plt
from cooptools import plotting as cplot
from cooptools import typeProviders as tp

logger = logging.getLogger(__name__)

def circ_arc_trajectory_planner(
    init_pos: vec.FloatVec,
    init_heading: vec.FloatVec,
    target_pos: vec.FloatVec,
    target_heading: vec.FloatVec,
    l: float,
    show_plot: bool=False,
    save_plot_filename_provider: tp.FilePathProvider = None
):
    x0x, x0y = init_pos
    v0x, v0y = init_heading
    xTx, xTy = target_pos
    vTx, vTy = target_heading

    x1 = vec.add_vectors([init_pos, vec.scaled_to_length(init_heading, l)])


    # We want to find the distance D that is the sum of straight line movement, followed by arc, and final straight line

    # The intersection point O of the lines [(x0, x0+v0), (xT, xT+vT)]
    O = lin.line_intersection_2d((init_pos, vec.add_vectors([init_pos, init_heading])),
                                 (target_pos, vec.add_vectors([target_pos, target_heading])),
                                 extend=True)
    logger.info(f"O: {O}")

    # The bisecting line between the two points and their intersection O is OG
    OX0_len = vec.distance_between(init_pos, O)
    OXT_len = vec.distance_between(target_pos, O)
    OX1_len = vec.distance_between(x1, O)

    scale = max(OXT_len, OX0_len, OX1_len)

    vOGx = (x0x - O[0]) / OX0_len + (xTx - O[0]) / OXT_len
    vOGy = (x0y - O[1]) / OX0_len + (xTy - O[1]) / OXT_len
    vOG = (vOGx, vOGy)
    vOG = vec.scaled_to_length(vOG, 1.5*scale)

    lOG = (O, vec.add_vectors([O, vOG]))
    logger.info(f"Line OG: {lOG}")

    # Calculate perp line to OX1 @ X1
    perp_line_at_x1 = lin.perp_line_to_line_at_point(x1, slope_int=lin.slope_intercept_form_from_points((O, init_pos)))
    perp_line_vector = vec.scaled_to_length((1, perp_line_at_x1[0]), scale)
    perp_line_pts = (x1, vec.add_vectors([x1, perp_line_vector]))

    # Center of circle, C, is the intersection of OG and perp(OX1@X1)
    C = lin.line_intersection_2d(perp_line_pts,
                                 lOG,
                                 extend=True)
    r = vec.distance_between(C, x1)
    circC = C, r


    # The traversed arc_angle is pi + the angle between the initial and target vector, omega
    omega = vec.rads_between(target_pos, init_pos, O)
    x_trans = (x1[0] - C[0])
    y_trans = (x1[1] - C[1])
    x2x = x_trans * math.cos(math.pi - omega) - y_trans * math.sin(math.pi - omega) + C[0]
    x2y = x_trans * math.sin(math.pi - omega) + y_trans * math.cos(math.pi - omega) + C[1]
    x2 = (x2x, x2y)
    traversed_arc_angle = omega + math.pi
    logger.info(f"Traversed arc angle: {traversed_arc_angle}")

    if show_plot or save_plot_filename_provider is not None:
        fig, ax = plt.subplots()
        cplot._plot(
            fig=fig,
            ax=ax,
            pts={init_pos: (('r+',), {}),
                 target_pos: (('b+',), {}),
                 O: (('g+',), {}),
                 x1: (('r+',), {}),
                 C: (('g+',), {}),
                 x2: (('r+',), {}),
                 # o2: (('g+',), {}),
                 },
            lines={
                (init_pos, O): ((), {'linestyle': 'dotted', 'color': 'grey'}),
                (init_pos, x1): ((), {'color': 'blue'}),
                (target_pos, O): ((), {'linestyle': 'dotted', 'color': 'grey'}),
                lOG: ((), {'linestyle': 'dotted', 'color': 'grey'}),
                perp_line_pts: ((), {'linestyle': 'dotted', 'color': 'grey'}),
                (x1, C): ((), {'linestyle': 'dotted', 'color': 'grey'}),
                (C, O): ((), {'linestyle': 'dotted', 'color': 'grey'}),
                (x2, target_pos): ((), {'color': 'blue'}),
                # ((desired_pt[0] - 3, line.eval(bisecting_line_1, desired_pt[0] - 3)),
                #  (desired_pt[0] + 3, line.eval(bisecting_line_1, desired_pt[0] + 3))): (
                #     (), {'linestyle': 'dotted', 'color': 'red'}),
                # ((desired_pt[0] - 3, line.eval(bisecting_line_2, desired_pt[0] - 3)),
                #  (desired_pt[0] + 3, line.eval(bisecting_line_2, desired_pt[0] + 3))): (
                #     (), {'linestyle': 'dotted', 'color': 'red'}),
                # (desired_pt, o1): ((), {'linestyle': 'dotted', 'color': 'blue'}),
                # (desired_pt, o2): ((), {'linestyle': 'dotted', 'color': 'blue'}),
            },
            circles={
                circC: ((), {'linestyle': 'dotted', 'edgecolor': 'blue', 'facecolor': 'none'}),
                # circ2: ((), {'linestyle': 'dotted', 'edgecolor': 'orange', 'facecolor': 'none'})
            },
            arrows={
                (target_pos, vec.scaled_to_length(target_heading, 10)): ((), {'color': 'black', 'length_includes_head': True, 'head_width': .3, 'linewidth': 1.5}),
                (init_pos, vec.scaled_to_length(init_heading, 10)): ((), {'color': 'black', 'length_includes_head': True, 'head_width': .3, 'linewidth': 1.5})
            },
            arcs={
                # (circC[0], circC[1], vec.rads(x1, circC[0]), vec.rads(x2, circC[0])): ((), {}),
                (circC[0], circC[1], vec.rads(x2, circC[0]), vec.rads(x1, circC[0])): ((), {})
            }
        )
        ax.set_aspect('equal', adjustable='box')  # Ensures the circle appears circular

        if save_plot_filename_provider is not None:
            fp = tp.resolve(save_plot_filename_provider)
            plt.savefig(fp)

        if show_plot:
            plt.show(block=True)


if __name__ == "__main__":
    from cooptools.loggingHelpers import BASE_LOG_FORMAT
    import random as rnd
    from cooptools import os_manip as osm

    logging.basicConfig(format=BASE_LOG_FORMAT, level=logging.INFO)

    def t01(
            init_pos,
            init_heading,
            target_pos,
            target_heading,
            l: float,
            plot: bool,
    ):
        circ_arc_trajectory_planner(
            init_pos=init_pos,
            init_heading=init_heading,
            target_pos=target_pos,
            target_heading=target_heading,
            plot=plot,
            l=l
        )


    def t02(test_count: int):
        boundary = 400, 400
        run_id = time.perf_counter()



        dir = fr"C:\Users\Tj Burns\Downloads\tst_trajectory"
        dir = fr"{dir}\{run_id}"
        osm.check_and_make_dirs(dir)

        l = rnd.uniform(0, 20)

        for ii in range(test_count):
            circ_arc_trajectory_planner(
                init_pos=(rnd.uniform(0, boundary[0]), rnd.uniform(0, boundary[0])),
                init_heading=vec.random_radial(len_boundary=(1, 10)),
                target_pos=(rnd.uniform(0, boundary[0]), rnd.uniform(0, boundary[0])),
                target_heading=vec.random_radial(len_boundary=(1, 10)),
                save_plot_filename_provider=fr"{dir}\{ii}.png",
                l=l
            )



    # t01(
    #     init_pos=(10, 20),
    #     init_heading=(1, 2),
    #     target_pos=(30, 1),
    #     target_heading=(-1, 0),
    #     plot=True,
    #     l=10
    # )
    #
    # t01(
    #     init_pos=(10, 20),
    #     init_heading=(-3, 2),
    #     target_pos=(30, 1),
    #     target_heading=(-1, 0),
    #     plot=True,
    #     l=10
    # )

    # t01(
    #     init_pos=(10, 20),
    #     init_heading=(-3, 2),
    #     target_pos=(30, 1),
    #     target_heading=(-1, -8),
    #     plot=True,
    #
    #     l=0
    # )

    t02(10)