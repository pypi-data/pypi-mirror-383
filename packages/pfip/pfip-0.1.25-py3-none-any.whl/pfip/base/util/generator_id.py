import threading
import time


class SnowflakeIdWorker:
    twepoch = 1288834974657  # 起始时间戳，这里假设为2010-11-04 09:42:54.657 UTC
    worker_id_bits = 5  # 机器id所占的位数
    datacenter_id_bits = 5  # 数据中心id所占的位数
    max_worker_id = -1 ^ (-1 << worker_id_bits)  # 可用的最大机器id，结果是31
    max_datacenter_id = -1 ^ (-1 << datacenter_id_bits)  # 可用的最大数据中心id，结果是31
    sequence_bits = 12  # 序列在id中占的位数
    worker_id_shift = sequence_bits  # 机器id向左移12位
    datacenter_id_shift = sequence_bits + worker_id_bits  # 数据中心id向左移17位(12+5)
    timestamp_left_shift = sequence_bits + worker_id_bits + datacenter_id_bits  # 时间截向左移22位(5+5+12)
    sequence_mask = -1 ^ (-1 << sequence_bits)  # 生成序列的掩码，这里为4095
    last_timestamp = -1  # 上次生成ID的时间截
    # 锁对象
    lock = threading.Lock()

    def __init__(self, datacenter_id, worker_id, sequence=0):
        if worker_id > self.max_worker_id or worker_id < 0:
            raise ValueError('worker_id值越界')
        if datacenter_id > self.max_datacenter_id or datacenter_id < 0:
            raise ValueError('datacenter_id值越界')
        self.datacenter_id = datacenter_id
        self.worker_id = worker_id
        self.sequence = sequence

    def _til_next_millis(self, last_timestamp):
        timestamp = int(time.time() * 1000)
        while timestamp <= last_timestamp:
            timestamp = int(time.time() * 1000)
        return timestamp

    def next_id(self):
        with self.lock:
            timestamp = int(time.time() * 1000)

            if self.last_timestamp == timestamp:
                self.sequence = (self.sequence + 1) & self.sequence_mask
                if self.sequence == 0:
                    timestamp = self._til_next_millis(self.last_timestamp)
            else:
                self.sequence = 0

            self.last_timestamp = timestamp

            return ((timestamp - self.twepoch) << self.timestamp_left_shift) | \
                (self.datacenter_id << self.datacenter_id_shift) | \
                (self.worker_id << self.worker_id_shift) | \
                self.sequence


id_generator = SnowflakeIdWorker(datacenter_id=10, worker_id=10)

if __name__ == '__main__':
    for _ in range(10):
        print(id_generator.next_id())
