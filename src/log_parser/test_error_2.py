import os
import re
from collections import defaultdict


def create_separate_error_files(input_file, output_folder="error_logs"):
    """
    Create separate text files for each unique namespace.
    Creates empty files for namespaces with no ERROR logs.

    Args:
        input_file: Path to the input log file
        output_folder: Folder where separate files will be created
    """
    try:
        # Create output folder if it doesn't exist
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
            print(f"Created output folder: '{output_folder}'")

        # Dictionary to store errors grouped by namespace
        error_groups = defaultdict(list)
        # Set to store all unique namespaces (regardless of log level)
        all_namespaces = set()

        # Read the log file
        with open(input_file, "r", encoding="utf-8") as infile:
            for line in infile:
                # Extract namespace for any log level (ERROR, INFO, WARN, etc.)
                match = re.search(
                    r"\[\d+\]\s+(ERROR|INFO|WARN|DEBUG|TRACE)\s+([\w\.]+)\s+-", line
                )
                if match:
                    log_level = match.group(1)
                    namespace = match.group(2)

                    # Add to all namespaces set
                    all_namespaces.add(namespace)

                    # If it's an ERROR, add to error_groups
                    if log_level == "ERROR":
                        error_groups[namespace].append(line.strip())

        # Create files for all namespaces
        file_count = 0
        error_file_count = 0
        empty_file_count = 0
        total_errors = 0

        for namespace in sorted(all_namespaces):
            # Create a safe filename from namespace
            safe_filename = namespace.replace(".", "_")
            output_file = os.path.join(output_folder, f"{safe_filename}.txt")

            logs = error_groups.get(namespace, [])

            # Write logs to separate file
            with open(output_file, "w", encoding="utf-8") as outfile:
                outfile.write("=" * 100 + "\n")
                outfile.write(f"ERROR LOGS FOR: {namespace}\n")
                outfile.write("=" * 100 + "\n")

                if logs:
                    outfile.write(f"Total errors: {len(logs)}\n")
                    outfile.write("=" * 100 + "\n\n")

                    for log in logs:
                        outfile.write(f"{log}\n")

                    outfile.write("\n" + "=" * 100 + "\n")
                    outfile.write(f"END OF LOG - Total: {len(logs)} error(s)\n")
                    error_file_count += 1
                    total_errors += len(logs)
                else:
                    outfile.write(f"Total errors: 0\n")
                    outfile.write("=" * 100 + "\n\n")
                    outfile.write("*** NO ERROR LOGS FOUND FOR THIS NAMESPACE ***\n\n")
                    outfile.write("=" * 100 + "\n")
                    empty_file_count += 1

                outfile.write("=" * 100 + "\n")

            file_count += 1
            status = f"({len(logs)} errors)" if logs else "(EMPTY)"
            print(f"Created: {output_file} {status}")

        # Create summary file
        summary_file = os.path.join(output_folder, "_SUMMARY.txt")
        with open(summary_file, "w", encoding="utf-8") as summary:
            summary.write("=" * 100 + "\n")
            summary.write("ERROR LOG SUMMARY\n")
            summary.write("=" * 100 + "\n\n")

            summary.write("NAMESPACES WITH ERRORS:\n")
            summary.write("-" * 100 + "\n")
            for namespace in sorted(error_groups.keys()):
                count = len(error_groups[namespace])
                summary.write(f"{namespace}\n")
                summary.write(f"  Count: {count} error(s)\n\n")

            summary.write("\n" + "=" * 100 + "\n\n")
            summary.write("NAMESPACES WITHOUT ERRORS:\n")
            summary.write("-" * 100 + "\n")
            namespaces_without_errors = sorted(
                all_namespaces - set(error_groups.keys())
            )
            if namespaces_without_errors:
                for namespace in namespaces_without_errors:
                    summary.write(f"{namespace}\n")
                    summary.write(f"  Count: 0 error(s)\n\n")
            else:
                summary.write("(None)\n\n")

            summary.write("=" * 100 + "\n")
            summary.write(f"Total unique namespaces: {file_count}\n")
            summary.write(f"Namespaces with errors: {error_file_count}\n")
            summary.write(f"Namespaces without errors: {empty_file_count}\n")
            summary.write(f"Total error logs: {total_errors}\n")
            summary.write("=" * 100 + "\n")

        print(f"\n{'=' * 60}")
        print(f"SUMMARY:")
        print(f"  Total files created: {file_count}")
        print(f"  Files with errors: {error_file_count}")
        print(f"  Empty files: {empty_file_count}")
        print(f"  Total errors processed: {total_errors}")
        print(f"  Output folder: '{output_folder}'")
        print(f"  Summary file: '{summary_file}'")
        print(f"{'=' * 60}")

    except FileNotFoundError:
        print(f"Error: File '{input_file}' not found!")
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    # Configuration - Change these to your file names
    input_log = "/home/dhruv/code/log_parser/2601/App/2026-01-24/App.log"  # Your input log file name
    output_folder = "error_logs"  # Folder where separate files will be created

    # Run the separation
    create_separate_error_files(input_log, output_folder)
