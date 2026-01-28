from log_parser.line_parser import read_log, write_sessions_to_file
import re


def main():
    output_file = "sessions.txt"

    folder_path = "/home/dhruv/code/log_parser/2601/App/2026-01-24/"

    log_file = folder_path + "App.log"

    sessions = read_log(log_file)
    write_sessions_to_file(sessions, output_file)

    print(f"{len(sessions)} sessions written to {output_file}")


if __name__ == "__main__":
    main()
