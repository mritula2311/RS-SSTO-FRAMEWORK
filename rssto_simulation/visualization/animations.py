import os
import numpy as np
import matplotlib

# Ensure non-interactive backend for headless generation
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from PIL import Image
import io


def _draw_static(ax, env):
    ax.set_xlim(0, env.width)
    ax.set_ylim(0, env.height)
    ax.set_aspect("equal")
    for obs in env.obstacles:
        rect = plt.Rectangle((obs.x, obs.y), obs.w, obs.h, color="black")
        ax.add_patch(rect)
    hazard = plt.Circle(env.hazard_pos, env.hazard_radius, color="red", alpha=0.3)
    exit_zone = plt.Circle(env.exit.pos, env.exit.radius, color="green", alpha=0.5)
    ax.add_patch(hazard)
    ax.add_patch(exit_zone)


def generate_animations(
    traces: dict,
    env,
    output_dir: str,
    save_gif: bool = True,
    save_mp4: bool = True,
    fps: int = 15,
    max_frames: int = 400,
):
    """Create per-algorithm animations from recorded position traces.

    Frames are downsampled for speed/size.
    Uses fast direct frame rendering with PIL for GIFs (much faster than matplotlib.animation.save).
    MP4 still uses ffmpeg if available.
    """
    if not traces:
        return
    os.makedirs(output_dir, exist_ok=True)
    ffmpeg_ok = animation.writers.is_available("ffmpeg")
    if save_mp4 and not ffmpeg_ok:
        print("[WARN] ffmpeg not available; skipping all MP4 exports")
        save_mp4 = False
    
    for name, frames in traces.items():
        if not frames:
            continue
        
        n_frames = len(frames)
        stride = max(1, n_frames // max_frames) if max_frames else 1
        frames_ds = frames[::stride]
        effective_fps = max(1.0, float(fps) / float(stride))
        
        print(f"[INFO] Generating animation for {name} ({len(frames)} frames, stride {stride})")
        
        base = name.replace(" ", "_").lower()
        
        try:
            if save_gif:
                # Fast GIF generation using direct frame rendering with PIL
                gif_path = os.path.join(output_dir, f"{base}.gif")
                _generate_gif_fast(frames_ds, env, name, gif_path, effective_fps)
                print(f"[INFO] Saved GIF: {gif_path}")
            
            if save_mp4:
                # MP4 generation using matplotlib animation (requires ffmpeg)
                mp4_path = os.path.join(output_dir, f"{base}.mp4")
                _generate_mp4(frames_ds, env, name, mp4_path, effective_fps)
                print(f"[INFO] Saved MP4: {mp4_path}")
                
        except Exception as exc:
            print(f"[WARN] Failed to save animation for {name}: {exc}")


def _generate_gif_fast(frames, env, name, output_path, fps):
    """Generate GIF by rendering frames directly (much faster than matplotlib.animation.save)."""
    fig, ax = plt.subplots(figsize=(6, 6), dpi=80)
    ax.set_title(f"{name} Evacuation")
    _draw_static(ax, env)
    scat = ax.scatter([], [], c="blue", s=18)
    
    pil_frames = []
    try:
        for i, frame_data in enumerate(frames):
            # Update scatter plot with current frame data
            scat.set_offsets(frame_data)
            
            # Render to buffer
            fig.canvas.draw()
            
            # Convert to PIL Image
            buf = fig.canvas.buffer_rgba()
            w, h = fig.canvas.get_width_height()
            img = Image.frombytes('RGBA', (w, h), buf)
            # Convert RGBA to RGB for GIF compatibility
            rgb_img = Image.new('RGB', img.size, (255, 255, 255))
            rgb_img.paste(img, mask=img.split()[3])  # Use alpha channel as mask
            pil_frames.append(rgb_img)
        
    finally:
        plt.close(fig)
    
    # Save as GIF using PIL
    if pil_frames:
        duration = int(1000 / fps)  # milliseconds per frame
        pil_frames[0].save(
            output_path,
            save_all=True,
            append_images=pil_frames[1:],
            duration=duration,
            loop=0,
            optimize=False,
            format='GIF'
        )
        # Close all PIL images
        for img in pil_frames:
            img.close()


def _generate_mp4(frames, env, name, output_path, fps):
    """Generate MP4 using matplotlib animation (requires ffmpeg)."""
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.set_title(f"{name} Evacuation")
    _draw_static(ax, env)
    scat = ax.scatter([], [], c="blue", s=18)

    def init():
        scat.set_offsets(np.empty((0, 2)))
        return scat,

    def update(idx):
        data = frames[idx]
        scat.set_offsets(data)
        return scat,

    anim = animation.FuncAnimation(
        fig,
        update,
        init_func=init,
        frames=len(frames),
        interval=1000 / fps,
        blit=True,
        repeat=False,
    )
    
    anim.save(output_path, writer="ffmpeg", fps=fps)
    plt.close(fig)

