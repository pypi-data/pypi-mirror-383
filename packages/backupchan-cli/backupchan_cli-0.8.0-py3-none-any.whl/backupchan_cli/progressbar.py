def update_progress_bar(file_index: int, total_files: int, file_name: str):
    percent = round(file_index / total_files * 100)
    print(f"\r{percent}% | file {file_index}/{total_files} {file_name}", end="")
