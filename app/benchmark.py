# import time
# import os
# import psutil
# from pymongo import MongoClient


# MONGO_URI = "mongodb://localhost:27017"
# DATABASE_NAME = "ecommerce_dummy_db"
# COLLECTION_NAME = "products"

# READ_COUNT = 1000
# WRITE_COUNT = 1000


# client = MongoClient(MONGO_URI)
# db = client[DATABASE_NAME]
# collection = db[COLLECTION_NAME]

# process = psutil.Process(os.getpid())


# def get_memory_mb():
#     memory = process.memory_info().rss
#     return memory / (1024 * 1024)


# def get_cpu_percent():
#     return process.cpu_percent(interval=0.5)


# def benchmark_read():
#     print("\n========== READ TEST ==========")

#     memory_before = get_memory_mb()

#     start_time = time.perf_counter()

#     documents = list(
#         collection.find({}).limit(READ_COUNT)
#     )

#     end_time = time.perf_counter()

#     memory_after = get_memory_mb()

#     elapsed = end_time - start_time

#     cpu = get_cpu_percent()

#     documents_fetched = len(documents)

#     throughput = (
#         documents_fetched / elapsed
#         if elapsed > 0
#         else 0
#     )

#     print(f"Documents fetched : {documents_fetched}")
#     print(f"Read time         : {elapsed:.4f} seconds")
#     print(f"Throughput        : {throughput:.2f} docs/sec")
#     print(f"CPU usage         : {cpu:.2f}%")
#     print(f"RAM before        : {memory_before:.2f} MB")
#     print(f"RAM after         : {memory_after:.2f} MB")
#     print(f"RAM difference    : {memory_after - memory_before:.2f} MB")


# def benchmark_write():
#     print("\n========== WRITE TEST ==========")

#     documents = []

#     for i in range(WRITE_COUNT):
#         documents.append(
#             {
#                 "benchmark": True,
#                 "student_number": i,
#                 "name": f"Benchmark Student {i}",
#                 "created_at": time.time()
#             }
#         )

#     memory_before = get_memory_mb()

#     start_time = time.perf_counter()

#     result = collection.insert_many(documents)

#     end_time = time.perf_counter()

#     memory_after = get_memory_mb()

#     elapsed = end_time - start_time

#     cpu = get_cpu_percent()

#     documents_inserted = len(result.inserted_ids)

#     throughput = (
#         documents_inserted / elapsed
#         if elapsed > 0
#         else 0
#     )

#     print(f"Documents inserted : {documents_inserted}")
#     print(f"Write time         : {elapsed:.4f} seconds")
#     print(f"Throughput         : {throughput:.2f} docs/sec")
#     print(f"CPU usage          : {cpu:.2f}%")
#     print(f"RAM before         : {memory_before:.2f} MB")
#     print(f"RAM after          : {memory_after:.2f} MB")
#     print(f"RAM difference     : {memory_after - memory_before:.2f} MB")


# def main():
#     print("======================================")
#     print("      MongoDB Performance Benchmark")
#     print("======================================")

#     print(f"Database   : {DATABASE_NAME}")
#     print(f"Collection : {COLLECTION_NAME}")

#     benchmark_read()
#     benchmark_write()

#     client.close()


# if __name__ == "__main__":
#     main()