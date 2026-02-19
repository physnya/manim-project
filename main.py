from manim_imports_ext import *
from scipy.integrate import solve_ivp
import numpy as np

# start
text1 = [
    """我们通常认为，大自然是完美的守序者.""",
    """如果没有外力干扰，生态系统似乎总能找到某种 “平衡”.\n\n
    兔子多了，草就少了；狐狸多了，兔子就少了，这一直是经典教科书告诉我们的故事.""",
    """但是 1991 年，两位生态学家 Hastings 和 Powell 在这个\n
    看似完美的数学模型中发现了一个隐藏的幽灵.\n\n
    用 x, y, z 表示植物、食草动物和食肉动物，他们描述了一个简单的食物链，\n
    并在其中加入了一些限制条件，比如植物按照某种称为 Logistic 映射的方式增长、\n
    动物和植物的死亡率不随着种群数量的变化而变化等等."""
]
class Main(InteractiveScene):
    def construct(self):
        script = []
        for line in text1:
            t = Text(
                line,
                font="LXGW Bright GB",
                font_size=32
            )
            script.append(t)
            
        for t in script:
            self.play(Write(t), run_time=len(t) / 50)
            self.wait(len(t) / 25)
            self.play(FadeOut(t), run_time=1)

text2 = [
    """上面是我们刚才所提到的那个描述食物链的方程."""
]
# Hastings-Powell (1991) 3 species food-chain model
def hastings_powell_system(t, state):
    x, y, z = state
    
    a1 = 5.0
    b1 = 3.0
    a2 = 0.1
    b2 = 2.0
    d1 = 0.4  # y death rate
    d2 = 0.01 # z death rate (key attribute)

    # plant x: Logistic breed - eaten by y (Holling II)
    dxdt = x * (1 - x) - (a1 * x * y) / (1 + b1 * x)
    
    # herbivore y: eat x (Holling II) - natural death - eaten by z (Holling II)
    dydt = (a1 * x * y) / (1 + b1 * x) - d1 * y - (a2 * y * z) / (1 + b2 * y)
    
    # carnivore z: eat y (Holling II) - natural death
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
    
    # exclude NaN/Inf
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
        
        script = []
        for line in text2:
            t = Text(
                line,
                font="LXGW Bright GB",
                font_size=30
            )
            script.append(t)
            
        for i in range(len(script)):
            script[i].fix_in_frame()
            script[i].to_edge(DOWN)
        
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
        self.play(
            Write(equations),
            Write(script[0]),
            run_time=2
        )
        equations.set_backstroke()
        
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

# Lorenz Attractor
def lorenz_system(t, state, sigma=10, rho=28, beta=8 / 3):
    x, y, z = state
    dxdt = sigma * (y - x)
    dydt = x * (rho - z) - y
    dzdt = x * y - beta * z
    return [dxdt, dydt, dzdt]


def ode_solution_points(function, state0, time, dt=0.01):
    solution = solve_ivp(
        function,
        t_span=(0, time),
        y0=state0,
        t_eval=np.arange(0, time, dt)
    )
    return solution.y.T


def for_later():
    tail = VGroup(
        TracingTail(dot, time_traced=3).match_color(dot)
        for dot in dots
    )

class LorenzAttractor(InteractiveScene):
    def construct(self):
        # Set up axes
        axes = ThreeDAxes(
            x_range=(-50, 50, 5),
            y_range=(-50, 50, 5),
            z_range=(-0, 50, 5),
            width=16,
            height=16,
            depth=8,
        )
        axes.set_width(FRAME_WIDTH)
        axes.center()

        self.frame.reorient(43, 76, 1, IN, 10)
        self.add(axes)

        # Add the equations
        equations = Tex(
            R"""
            \begin{aligned}
            \frac{\mathrm{d} x}{\mathrm{d} t} & =\sigma(y-x) \\
            \frac{\mathrm{d} y}{\mathrm{d} t} & =x(\rho-z)-y \\
            \frac{\mathrm{d} z}{\mathrm{d} t} & =x y-\beta z
            \end{aligned}
            """,
            t2c={
                "x": RED,
                "y": GREEN,
                "z": BLUE,
            },
            font_size=30
        )
        equations.fix_in_frame()
        equations.to_corner(UL)
        equations.set_backstroke()
        
        self.play(Write(equations), run_time=2)

        epsilon = 1e-5
        evolution_time = 20
        n_points = 10
        
        states = [
            [10, 10, 10 + n * epsilon]
            for n in range(n_points)
        ]
        colors = color_gradient([BLUE, GREEN], len(states))

        curves = VGroup()
        for state in states:
            points = ode_solution_points(lorenz_system, state, evolution_time, dt=0.01)

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
            self.frame.animate.reorient(43, 76, 1, IN, 10).move_to(end_center).set_height(8),
            *[FadeOut(curve) for curve in curves],
            *[FadeOut(equations)],
            run_time=4
        )
        
        self.wait(2)