import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button
from matplotlib.colors import hsv_to_rgb
import os

# ==================== 全局设置 —— 修复中文方块问题 ====================
plt.rcParams['font.family'] = ['DejaVu Sans', 'SimHei', 'Microsoft YaHei', 'WenQuanYi Micro Hei']
plt.rcParams['axes.unicode_minus'] = False

# ==================== 物理参数 ====================
d1 = 1.0
wl_init = 550.0
d2_init = 2.0
d2_min = 0.0
d2_max = 4.0    # 动镜范围变小：0 ~ 4 μm
d2_step = 0.01

# ==================== 画布布局 ====================
fig = plt.figure(figsize=(14, 10))
fig.subplots_adjust(left=0.08, right=0.95, top=0.92, bottom=0.20, wspace=0.25)

# 保存图像按钮
ax_btn_save = fig.add_axes([0.08, 0.94, 0.12, 0.04])
btn_save = Button(ax_btn_save, 'Save Image', color='#e8f8f0')

# 新增：显示/隐藏文字按钮（放在保存按钮正下方）
ax_btn_toggle_text = fig.add_axes([0.08, 0.89, 0.12, 0.04])
btn_toggle_text = Button(ax_btn_toggle_text, 'Show/Hide Text', color='#f8f0e8')

# 光路图
ax_optics = fig.add_axes([0.08, 0.18, 0.34, 0.74])
ax_optics.set_xlim(-3.0, d2_max + 1.0)
ax_optics.set_ylim(-3.0, 4.5)
ax_optics.set_aspect('equal')
ax_optics.grid(True, linestyle='--', alpha=0.3)
ax_optics.set_title("Michelson Interferometer - Optical Path")
ax_optics.set_xlabel("x (μm)")
ax_optics.set_ylabel("y (μm)")

# 干涉条纹图
ax_fringes = fig.add_axes([0.55, 0.52, 0.35, 0.36])
ax_fringes.set_xlim(-1, 1)
ax_fringes.set_ylim(-1, 1)
ax_fringes.set_aspect('equal')
ax_fringes.set_title("Interference Fringes")

# 光强分布图
ax_intensity = fig.add_axes([0.55, 0.28, 0.35, 0.16])
ax_intensity.set_xlim(-1, 1)
ax_intensity.set_ylim(0, 1.05)
ax_intensity.set_title("Intensity Profile")
ax_intensity.grid(True, linestyle='--', alpha=0.3)

# ==================== 滑块 ====================
ax_slider_wl = fig.add_axes([0.12, 0.12, 0.76, 0.03])
ax_slider_d2 = fig.add_axes([0.12, 0.07, 0.76, 0.03])

slider_wl = Slider(ax_slider_wl, 'Wavelength (nm)', 400, 700, valinit=wl_init, valstep=1)
slider_d2 = Slider(ax_slider_d2, 'M2 Position (μm)', d2_min, d2_max, valinit=d2_init, valstep=d2_step)

# ==================== 元器件放大 ====================
# 分光镜（加大）
bs_line, = ax_optics.plot([-0.6, 0.6], [-0.6, 0.6], 'k-', lw=3)

# 固定镜 M1（加大、加粗）
m1_line, = ax_optics.plot([-0.8, 0.8], [2.0, 2.0], 'b-', lw=5, label='M1 fixed')

# 动镜 M2（加大、加粗）
m2_line, = ax_optics.plot([d2_init, d2_init], [-0.8, 0.8], 'r-', lw=5, label='M2 movable')
m2_label = ax_optics.text(d2_init + 0.2, 0, f'M2', color='red', fontsize=12, weight='bold')

# 屏幕（加大）
screen_line, = ax_optics.plot([-1.0, 1.0], [-1.2, -1.2], 'g-', lw=5, label='Screen')

# 光源点（加大）
ax_optics.plot(-2.5, 0, 'yo', markersize=14)

# 光线（加粗）
ray_source_bs, = ax_optics.plot([-2.5, 0], [0, 0], 'k-', lw=2.5)
ray_bs_m1_up, = ax_optics.plot([0, 0], [0, 2.0], 'k-', lw=2.5)
ray_m1_bs_down, = ax_optics.plot([0, 0], [2.0, 0], 'k--', lw=2.5)
ray_bs_m2_right, = ax_optics.plot([0, d2_init], [0, 0], 'k-', lw=2.5)
ray_m2_bs_left, = ax_optics.plot([d2_init, 0], [0, 0], 'k--', lw=2.5)
ray_screen, = ax_optics.plot([0, 0], [0, -1.2], 'm-', lw=2.5)

ax_optics.legend(loc='upper left', fontsize=11)

# ==================== 干涉计算 ====================
N = 400
x = np.linspace(-1, 1, N)
y = np.linspace(-1, 1, N)
X, Y = np.meshgrid(x, y)
R = np.sqrt(X**2 + Y**2)
f_lens = 0.5
cos_theta = 1 / np.sqrt(1 + (R / f_lens)**2)

def wavelength_to_rgb_vec(wl_nm, intensity):
    hue = 0.7 - 0.7 * (wl_nm - 400) / 300
    hue = np.clip(hue, 0.0, 0.7)
    hsv = np.stack([np.full_like(intensity, hue), np.ones_like(intensity), intensity], axis=-1)
    return hsv_to_rgb(hsv)

wl_um = wl_init / 1000
delta_init = 2 * (d2_init - d1)
phase_init = 2 * np.pi * delta_init * cos_theta / wl_um
I_init = 0.5 * (1 + np.cos(phase_init))
rgb_init = wavelength_to_rgb_vec(wl_init, I_init)
im = ax_fringes.imshow(rgb_init, extent=[-1, 1, -1, 1], origin='lower')

profile_init = 0.5 * (1 + np.cos(2 * np.pi * delta_init / wl_um / np.sqrt(1 + (x/f_lens)**2)))
line_profile, = ax_intensity.plot(x, profile_init, 'b-', lw=2)

info_text = ax_fringes.text(0.02, 0.98, '', transform=ax_fringes.transAxes,
                            verticalalignment='top', fontsize=10,
                            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.7))

# 文字显示状态标记
text_visible = True

# ==================== 保存图像函数 ====================
def save_interference_image(event):
    """保存当前的干涉条纹图像为PNG文件"""
    filename = f"干涉图像_{slider_wl.val:.0f}nm_{slider_d2.val:.2f}μm.png"
    extent = ax_fringes.get_window_extent().transformed(fig.dpi_scale_trans.inverted())
    fig.savefig(filename, bbox_inches=extent, dpi=300, facecolor='white')
    print(f"✅ 图像已保存：{filename}")

btn_save.on_clicked(save_interference_image)

# ==================== 显示/隐藏文字函数 ====================
def toggle_info_text(event):
    global text_visible
    text_visible = not text_visible
    info_text.set_visible(text_visible)
    fig.canvas.draw_idle()

btn_toggle_text.on_clicked(toggle_info_text)

# ==================== 更新函数 ====================
def update(val=None):
    wl = slider_wl.val
    d2 = slider_d2.val

    m2_line.set_data([d2, d2], [-0.8, 0.8])
    m2_label.set_x(d2 + 0.2)
    ray_bs_m2_right.set_data([0, d2], [0, 0])
    ray_m2_bs_left.set_data([d2, 0], [0, 0])

    norm = plt.Normalize(400, 700)
    color = plt.cm.rainbow(norm(wl))
    for line in [ray_source_bs, ray_bs_m1_up, ray_m1_bs_down, ray_bs_m2_right, ray_m2_bs_left, ray_screen]:
        line.set_color(color)

    wl_um = wl / 1000
    delta = 2 * (d2 - d1)
    phase = 2 * np.pi * delta * cos_theta / wl_um
    I = 0.5 * (1 + np.cos(phase))
    rgb = wavelength_to_rgb_vec(wl, I)
    im.set_data(rgb)

    profile = 0.5 * (1 + np.cos(2 * np.pi * delta / wl_um / np.sqrt(1 + (x/f_lens)**2)))
    line_profile.set_ydata(profile)

    info_text.set_text(f'OPD: {delta:.2f} μm\nλ: {wl:.0f} nm')

    fig.canvas.draw_idle()

slider_wl.on_changed(update)
slider_d2.on_changed(update)
update(None)
plt.show()