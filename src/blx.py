from prefect.filesystems import LocalFileSystem
from prefect.infrastructure import Process

# Create block
my_storage_block = LocalFileSystem(basepath="~/my-block")
my_storage_block.save(name="demo-storage-block", overwrite=True)

# Create process
my_process_infra = Process(working_dir="~/work")
my_process_infra.save(name="process-infra", overwrite=True)