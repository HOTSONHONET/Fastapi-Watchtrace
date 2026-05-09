from watchtrace.indexer import build_and_save_code_index

if __name__ == "__main__":
    build_and_save_code_index(
        root_dir="examples",
        output_file=".watchtrace/code_index.json",
    )
    print("Code index generated at .watchtrace/code_index.json")