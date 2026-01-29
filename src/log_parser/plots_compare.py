import matplotlib.pyplot as plt
import os

# ============================================================================
# EDIT THESE FILE PATHS
# ============================================================================
SESSION_23_PATH = "/home/dhruvkumarjiguda/code/log_parser/sessions_23.txt"
SESSION_24_PATH = "/home/dhruvkumarjiguda/code/log_parser/sessions_24.txt"
# ============================================================================


def parse_session_file(filepath):
    """Parse session data from txt file"""
    sessions = []
    current_session = {}

    with open(filepath, "r") as f:
        for line in f:
            line = line.strip()

            if line.startswith("Session"):
                if (
                    current_session
                    and current_session.get("pallets", 0) > 0
                    and "uph" in current_session
                ):
                    sessions.append(current_session)
                current_session = {"session_id": int(line.split()[1])}
            elif ":" in line and not line.startswith("-"):
                key, value = line.split(":", 1)
                key = key.strip()
                value = value.strip()

                if key == "Start Time":
                    current_session["start_time"] = value
                elif key == "Pallets Produced":
                    current_session["pallets"] = int(value)
                elif key == "UPH" and value != "None":
                    current_session["uph"] = float(value)
                elif key == "Seconds per Pallet" and value != "None":
                    current_session["sec_per_pallet"] = float(value)
                elif key == "Final Rolling UPH" and value != "None":
                    current_session["rolling_uph"] = int(value)

    # Add last session if valid
    if (
        current_session
        and current_session.get("pallets", 0) > 0
        and "uph" in current_session
    ):
        sessions.append(current_session)

    return sessions


def plot_rolling_uph(sessions, ax, title):
    """Plot Rolling UPH vs Calculated UPH"""
    session_ids = [s["session_id"] for s in sessions]
    calc_uph = [s["uph"] for s in sessions]
    rolling_uph = [s["rolling_uph"] for s in sessions]

    ax.plot(
        session_ids, calc_uph, "o-", label="Calculated UPH", linewidth=2, markersize=8
    )
    ax.plot(
        session_ids,
        rolling_uph,
        "s-",
        label="Rolling UPH (System)",
        linewidth=2,
        markersize=8,
        alpha=0.7,
    )
    ax.set_xlabel("Session ID", fontsize=12)
    ax.set_ylabel("UPH (Units Per Hour)", fontsize=12)
    ax.set_title(
        f"{title}\nRolling UPH vs Calculated UPH", fontsize=14, fontweight="bold"
    )
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)


def plot_pallets_produced(sessions, ax, title):
    """Plot Pallets Produced per Session (horizontal bars)"""
    session_ids = [s["session_id"] for s in sessions]
    pallets = [s["pallets"] for s in sessions]

    # Horizontal bar chart
    ax.barh(session_ids, pallets, color="steelblue", alpha=0.7)
    ax.set_ylabel("Session ID", fontsize=12)
    ax.set_xlabel("Pallets Produced", fontsize=12)
    ax.set_title(
        f"{title}\nPallets Produced per Session", fontsize=14, fontweight="bold"
    )
    ax.grid(True, alpha=0.3, axis="x")
    ax.invert_yaxis()  # Highest session ID at top


def create_uph_comparison(sessions_23, sessions_24, output_filename):
    """Create side-by-side Rolling UPH comparison"""

    if not sessions_23 or not sessions_24:
        print("Need both session files to create comparison")
        return

    # Create figure with 1x2 subplots
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))

    # Rolling UPH plots
    plot_rolling_uph(sessions_23, axes[0], "2026-01-23")
    plot_rolling_uph(sessions_24, axes[1], "2026-01-24")

    plt.suptitle(
        "Rolling UPH Comparison: 2026-01-23 vs 2026-01-24",
        fontsize=16,
        fontweight="bold",
        y=1.00,
    )
    plt.tight_layout()
    plt.savefig(output_filename, dpi=300, bbox_inches="tight")
    print(f"UPH comparison plot saved to {output_filename}")


def create_pallets_comparison(sessions_23, sessions_24, output_filename):
    """Create side-by-side Pallets Produced comparison"""

    if not sessions_23 or not sessions_24:
        print("Need both session files to create comparison")
        return

    # Create figure with 1x2 subplots
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))

    # Pallets Produced plots
    plot_pallets_produced(sessions_23, axes[0], "2026-01-23")
    plot_pallets_produced(sessions_24, axes[1], "2026-01-24")

    plt.suptitle(
        "Pallets Produced Comparison: 2026-01-23 vs 2026-01-24",
        fontsize=16,
        fontweight="bold",
        y=1.00,
    )
    plt.tight_layout()
    plt.savefig(output_filename, dpi=300, bbox_inches="tight")
    print(f"Pallets comparison plot saved to {output_filename}")


def create_individual_plot(sessions, output_filename, title, plot_type="rolling_uph"):
    """Create individual plot"""

    if not sessions:
        print(f"No valid sessions with UPH data found")
        return

    fig, ax = plt.subplots(1, 1, figsize=(10, 6))

    if plot_type == "rolling_uph":
        plot_rolling_uph(sessions, ax, title)
    elif plot_type == "pallets_produced":
        plot_pallets_produced(sessions, ax, title)

    plt.tight_layout()
    plt.savefig(output_filename, dpi=300, bbox_inches="tight")
    print(f"Individual plot saved to {output_filename}")


# Main execution
if __name__ == "__main__":
    sessions_23 = None
    sessions_24 = None

    # Load session files
    if os.path.exists(SESSION_23_PATH):
        print(f"Loading {SESSION_23_PATH}...")
        sessions_23 = parse_session_file(SESSION_23_PATH)
        print(f"  Found {len(sessions_23)} productive sessions")
    else:
        print(f"File not found: {SESSION_23_PATH}")

    if os.path.exists(SESSION_24_PATH):
        print(f"Loading {SESSION_24_PATH}...")
        sessions_24 = parse_session_file(SESSION_24_PATH)
        print(f"  Found {len(sessions_24)} productive sessions")
    else:
        print(f"File not found: {SESSION_24_PATH}")

    # Create separate comparison plots
    if sessions_23 and sessions_24:
        print("\nCreating UPH comparison...")
        create_uph_comparison(sessions_23, sessions_24, "uph_comparison.png")

        print("Creating Pallets comparison...")
        create_pallets_comparison(sessions_23, sessions_24, "pallets_comparison.png")

    # Create individual plots if you want them
    # Uncomment these lines to create individual plots:

    # if sessions_23:
    #     create_individual_plot(sessions_23, "rolling_uph_23.png", "2026-01-23", "rolling_uph")
    #     create_individual_plot(sessions_23, "pallets_23.png", "2026-01-23", "pallets_produced")

    # if sessions_24:
    #     create_individual_plot(sessions_24, "rolling_uph_24.png", "2026-01-24", "rolling_uph")
    #     create_individual_plot(sessions_24, "pallets_24.png", "2026-01-24", "pallets_produced")

    print("\nDone!")
