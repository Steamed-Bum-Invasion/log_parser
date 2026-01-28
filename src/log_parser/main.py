from log_parser.line_parser import read_log, write_sessions_to_file
import re


def main():
    output_file_23 = "sessions_23.txt"
    output_file_24 = "sessions_24.txt"

    folder_24 = "/home/dhruvkumarjiguda/code/log_parser/2601/App/2026-01-24/"
    folder_23 = "/home/dhruvkumarjiguda/code/log_parser/2601/App/2026-01-23/"

    log_file_24 = folder_24 + "App.log"
    log_file_23 = folder_23 + "App.log"

    session_23 = read_log(log_file_23)
    session_24 = read_log(log_file_24)
    write_sessions_to_file(session_23, output_file_23)
    write_sessions_to_file(session_24, output_file_24)

    print(f"{len(session_23)} sessions written to {output_file_23}")
    print(f"{len(session_24)} sessions written to {output_file_24}")


if __name__ == "__main__":
    main()
