import matplotlib.pyplot as plt
import os

# ============================================================================
# EDIT THESE FILE PATHS - Just change these two lines
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


def create_analysis_plots(sessions, output_filename, title_prefix):
    """Create comprehensive analysis plots"""

    if not sessions:
        print(f"No valid sessions with UPH data found in {title_prefix}")
        return

    # Extract data for plotting
    session_ids = [s["session_id"] for s in sessions]
    calc_uph = [s["uph"] for s in sessions]
    rolling_uph = [s["rolling_uph"] for s in sessions]
    pallets = [s["pallets"] for s in sessions]
    sec_per_pallet = [s["sec_per_pallet"] for s in sessions]

    # Create figure with multiple subplots
    fig = plt.figure(figsize=(16, 10))

    # 1. Rolling UPH vs Calculated UPH
    ax1 = plt.subplot(2, 3, 1)
    ax1.plot(
        session_ids, calc_uph, "o-", label="Calculated UPH", linewidth=2, markersize=8
    )
    ax1.plot(
        session_ids,
        rolling_uph,
        "s-",
        label="Rolling UPH (System)",
        linewidth=2,
        markersize=8,
        alpha=0.7,
    )
    ax1.set_xlabel("Session ID", fontsize=12)
    ax1.set_ylabel("UPH (Units Per Hour)", fontsize=12)
    ax1.set_title("Rolling UPH vs Calculated UPH", fontsize=14, fontweight="bold")
    ax1.legend(fontsize=10)
    ax1.grid(True, alpha=0.3)

    # 2. Pallets Produced per Session
    ax2 = plt.subplot(2, 3, 2)
    bars = ax2.bar(session_ids, pallets, color="steelblue", alpha=0.7)
    ax2.set_xlabel("Session ID", fontsize=12)
    ax2.set_ylabel("Pallets Produced", fontsize=12)
    ax2.set_title("Pallets Produced per Session", fontsize=14, fontweight="bold")
    ax2.grid(True, alpha=0.3, axis="y")

    # 3. Seconds per Pallet
    ax3 = plt.subplot(2, 3, 3)
    ax3.plot(
        session_ids, sec_per_pallet, "o-", color="orange", linewidth=2, markersize=8
    )
    ax3.set_xlabel("Session ID", fontsize=12)
    ax3.set_ylabel("Seconds per Pallet", fontsize=12)
    ax3.set_title("Cycle Time per Pallet", fontsize=14, fontweight="bold")
    ax3.grid(True, alpha=0.3)
    avg_spp = sum(sec_per_pallet) / len(sec_per_pallet)
    ax3.axhline(
        y=avg_spp,
        color="red",
        linestyle="--",
        label=f"Average: {avg_spp:.2f}s",
        linewidth=2,
    )
    ax3.legend(fontsize=10)

    # 4. UPH vs Pallets Produced (Scatter)
    ax4 = plt.subplot(2, 3, 4)
    scatter = ax4.scatter(
        pallets, calc_uph, c=session_ids, cmap="viridis", s=100, alpha=0.6
    )
    ax4.set_xlabel("Pallets Produced", fontsize=12)
    ax4.set_ylabel("Calculated UPH", fontsize=12)
    ax4.set_title("UPH vs Production Volume", fontsize=14, fontweight="bold")
    ax4.grid(True, alpha=0.3)
    plt.colorbar(scatter, ax=ax4, label="Session ID")

    # 5. UPH Difference (Calculated - Rolling)
    ax5 = plt.subplot(2, 3, 5)
    uph_diff = [calc - roll for calc, roll in zip(calc_uph, rolling_uph)]
    colors = ["green" if d >= 0 else "red" for d in uph_diff]
    ax5.bar(session_ids, uph_diff, color=colors, alpha=0.6)
    ax5.axhline(y=0, color="black", linestyle="-", linewidth=1)
    ax5.set_xlabel("Session ID", fontsize=12)
    ax5.set_ylabel("UPH Difference (Calc - Rolling)", fontsize=12)
    ax5.set_title("Performance vs System Target", fontsize=14, fontweight="bold")
    ax5.grid(True, alpha=0.3, axis="y")

    # 6. Production Efficiency Distribution
    ax6 = plt.subplot(2, 3, 6)
    ax6.hist(calc_uph, bins=10, color="skyblue", alpha=0.7, edgecolor="black")
    avg_uph = sum(calc_uph) / len(calc_uph)
    ax6.axvline(
        x=avg_uph,
        color="red",
        linestyle="--",
        label=f"Mean: {avg_uph:.2f}",
        linewidth=2,
    )
    ax6.set_xlabel("Calculated UPH", fontsize=12)
    ax6.set_ylabel("Frequency", fontsize=12)
    ax6.set_title("UPH Distribution", fontsize=14, fontweight="bold")
    ax6.legend(fontsize=10)
    ax6.grid(True, alpha=0.3, axis="y")

    plt.suptitle(
        f"{title_prefix} - Session Analysis", fontsize=16, fontweight="bold", y=1.00
    )
    plt.tight_layout()
    plt.savefig(output_filename, dpi=300, bbox_inches="tight")
    print(f"Plot saved to {output_filename}")

    # Print summary statistics
    print("\n" + "=" * 60)
    print(f"{title_prefix} - SUMMARY STATISTICS")
    print("=" * 60)
    print(f"Total Sessions Analyzed: {len(sessions)}")
    print(f"Total Pallets Produced: {sum(pallets)}")
    print(f"\nCalculated UPH:")
    print(f"  Average: {avg_uph:.2f}")
    print(
        f"  Min: {min(calc_uph):.2f} (Session {session_ids[calc_uph.index(min(calc_uph))]})"
    )
    print(
        f"  Max: {max(calc_uph):.2f} (Session {session_ids[calc_uph.index(max(calc_uph))]})"
    )
    print(f"\nRolling UPH (System):")
    avg_rolling = sum(rolling_uph) / len(rolling_uph)
    print(f"  Average: {avg_rolling:.2f}")
    print(f"  Min: {min(rolling_uph)}")
    print(f"  Max: {max(rolling_uph)}")
    print(f"\nCycle Time (Seconds per Pallet):")
    print(f"  Average: {avg_spp:.2f}s")
    print(
        f"  Best: {min(sec_per_pallet):.2f}s (Session {session_ids[sec_per_pallet.index(min(sec_per_pallet))]})"
    )
    print(
        f"  Worst: {max(sec_per_pallet):.2f}s (Session {session_ids[sec_per_pallet.index(max(sec_per_pallet))]})"
    )
    print("=" * 60 + "\n")


# Main execution
if __name__ == "__main__":
    # Process sessions_23.txt
    if os.path.exists(SESSION_23_PATH):
        print(f"Processing {SESSION_23_PATH}...")
        sessions_23 = parse_session_file(SESSION_23_PATH)
        create_analysis_plots(
            sessions_23, 
            "session_analysis_23.png",  # Save in current directory
            "2026-01-23"
        )
    else:
        print(f"File not found: {SESSION_23_PATH}")

    # Process sessions_24.txt
    if os.path.exists(SESSION_24_PATH):
        print(f"Processing {SESSION_24_PATH}...")
        sessions_24 = parse_session_file(SESSION_24_PATH)
        create_analysis_plots(
            sessions_24, 
            "session_analysis_24.png",  # Save in current directory
            "2026-01-24"
        )
    else:
        print(f"File not found: {SESSION_24_PATH}")
    
    print("\nDone! Check the current directory for the PNG files.")
