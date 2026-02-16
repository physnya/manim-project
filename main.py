from manim_imports_ext import *
from scipy.integrate import solve_ivp
import numpy as np

# Hastings-Powell (1991) 3 物种食物链模型
def hastings_powell_system(t, state):
    x, y, z = state
    
    a1 = 5.0
    b1 = 3.0
    a2 = 0.1
    b2 = 2.0
    d1 = 0.4  # y 的死亡率
    d2 = 0.01 # z 的死亡率 (这是控制混沌分岔的关键参数)

    # 1. 植被 x: 逻辑斯蒂增长 - 被 y 捕食 (Holling II)
    dxdt = x * (1 - x) - (a1 * x * y) / (1 + b1 * x)
    
    # 2. 食草动物 y: 捕食 x (Holling II) - 自然死亡 - 被 z 捕食 (Holling II)
    dydt = (a1 * x * y) / (1 + b1 * x) - d1 * y - (a2 * y * z) / (1 + b2 * y)
    
    # 3. 食肉动物 z: 捕食 y (Holling II) - 自然死亡
    dzdt = (a2 * y * z) / (1 + b2 * y) - d2 * z
    
    return [dxdt, dydt, dzdt]

def ode_solution_points(function, state0, time, dt=0.01):
    solution = solve_ivp(
        function,
        t_span=(0, time),
        y0=state0,
        t_eval=np.arange(0, time, dt),
        method='RK45'
    )
    
    points = solution.y.T
    
    # 简单的 NaN/Inf 过滤
    if np.any(np.isnan(points)) or np.any(np.isinf(points)):
        points = points[~np.isnan(points).any(axis=1)]
        points = points[~np.isinf(points).any(axis=1)]
        
    return points

class EcologicChaos(InteractiveScene):
    def construct(self):
        axes = ThreeDAxes(
            x_range=(0, 1.2, 0.2),
            y_range=(0, 0.5, 0.1),
            z_range=(0, 15, 2),
            width=10,
            height=10,
            depth=8,
        )
        axes.shift(2 * DL)
        
        self.frame.reorient(135, 40, 0, IN, 10)
        self.frame.move_to(axes.c2p(0.5, 0.2, 5))

        equations = Tex(
            R"""
            \begin{aligned}
            \frac{\mathrm{d}x}{\mathrm{d}t} &= x(1-x) - \frac{a_1 xy}{1+b_1 x} \\
            \frac{\mathrm{d}y}{\mathrm{d}t} &= \frac{a_1 xy}{1+b_1 x} - d_1 y - \frac{a_2 yz}{1+b_2 y} \\
            \frac{\mathrm{d}z}{\mathrm{d}t} &= \frac{a_2 yz}{1+b_2 y} - d_2 z
            \end{aligned}
            """,
            t2c={
                "x": RED,
                "y": GREEN,
                "z": BLUE,
            },
            font_size=28
        )
        equations.fix_in_frame()
        equations.move_to(ORIGIN)
        equations.set_backstroke()
        
        self.play(Write(equations), run_time=2)
        self.wait(1)
        
        self.play(
            equations.animate.to_corner(UL),
            *[FadeIn(axes)],
            run_time=1.5
        )

        epsilon = 1e-3
        evolution_time = 400
        n_points = 12
        
        base_state = [0.8, 0.2, 8.0] 
        states = [
            [0.8, 0.2, 8.0 + n * epsilon]
            for n in range(n_points)
        ]
        
        colors = color_gradient([BLUE, GREEN], len(states))

        curves = VGroup()
        for state in states:
            points = ode_solution_points(hastings_powell_system, state, evolution_time, dt=0.05)

            curve = VMobject()
            curve.set_points_as_corners(axes.c2p(*points.T))
            curve.set_stroke(WHITE, 1.5, opacity=0.5)

            curve.set_fill(color=None, opacity=0)
            
            curves.add(curve)

        dots = Group(GlowDot(color=c, radius=0.16) for c in colors)
        
        for dot in dots:
            dot.move_to(curve.get_start())

        def update_dots(dots):
            for dot, curve in zip(dots, curves):
                if curve.get_num_points() > 0:
                    dot.move_to(curve.get_end())
        
        dots.add_updater(update_dots)

        self.add(dots)

        self.play(
            *(ShowCreation(curve, rate_func=linear) for curve in curves),
            run_time=20,
        )
        
        end_center = dots.get_center()
        dots.remove_updater(update_dots)
        
        self.play(
            self.frame.animate.reorient(100, 70, 0, IN, 10).move_to(end_center).set_height(8),
            *[FadeOut(curve) for curve in curves],
            *[FadeOut(equations)],
            run_time=4
        )
        
        self.wait(2)