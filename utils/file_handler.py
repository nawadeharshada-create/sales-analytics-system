# utils/file_handler.py

def read_sales_data(file_path):
    """
    Reads raw sales data from file
    Returns list of raw lines
    """
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            lines = file.readlines()

        # Remove empty lines and strip newline characters
        return [line.strip() for line in lines if line.strip()]

    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return []

    except Exception as e:
        print(f"Error reading file: {e}")
        return []
