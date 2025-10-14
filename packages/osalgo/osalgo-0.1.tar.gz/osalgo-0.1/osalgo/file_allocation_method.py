class SequentialFileAllocation:
    def __init__(self, total_blocks):
        self.total_blocks = total_blocks
        self.disk = [-1] * total_blocks

    def allocate_file(self, file_name, start_block, file_size):
        if start_block + file_size > self.total_blocks:
            return f"Error: Not enough space to allocate {file_name}."
        for i in range(start_block, start_block + file_size):
            if self.disk[i] != -1:
                return f"Error: Block {i} is already occupied. Cannot allocate {file_name}."
        for i in range(start_block, start_block + file_size):
            self.disk[i] = file_name
        return f"File '{file_name}' allocated from block {start_block} to block {start_block + file_size - 1}."

    def display_disk(self):
        print("Disk Status:")
        for i, block in enumerate(self.disk):
            print(f"Block {i}: {'Free' if block == -1 else block}")

# if __name__ == "__main__":
#     total_blocks = 10
#     file_system = SequentialFileAllocation(total_blocks)
#     print(file_system.allocate_file("File1", 2, 4))
#     print(file_system.allocate_file("File2", 6, 3))
#     print(file_system.allocate_file("File3", 8, 2))
#     file_system.display_disk()
