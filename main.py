import asyncio, math
from itertools import product


class Trivial:
    def __init__(self, n):
        self.n = n
        self.queue = asyncio.Queue(1)

    async def Alice(self, alpha):
        for i in range(1, self.n + 1):
            x = alpha[i]
            print("Alice send:   ", x)
            await self.queue.put(x)
            await asyncio.sleep(0)

        index = ""
        for i in range(self.n):
            bit_of_index = await self.queue.get()
            print("Alice receive index:", bit_of_index)
            index += bit_of_index

        print()
        print("Alice thinks that index is:", int(index, 2) + 1)

    async def Bob(self, beta):
        for i in range(1, self.n + 1):
            a = await self.queue.get()
            print("Bob receive:  ", a)

            if beta[i] != a:
                index = i

        print()
        index = bin(index - 1)[2:].zfill(self.n)
        for i in range(self.n):
            print("Bob send index:     ", index[i])
            await self.queue.put(index[i])
            await asyncio.sleep(0)

        print("Bob thinks that index is:  ", int(index, 2) + 1)


class Simple:
    def __init__(self, n):
        self.n = n
        self.queue = asyncio.Queue(1)

    async def Alice(self, alpha):
        lock_A = 0
        last_1_a = 0
        last_1_b = 0

        x = alpha[1]
        print("Alice send:   ", x)
        await self.queue.put(x)
        await asyncio.sleep(0)

        for i in range(2, self.n, 2):
            b = await self.queue.get()
            print("Alice receive:", b)
            if b == 1:
                last_1_b = i

            if lock_A == 1:
                x = 0
            else:
                if alpha[i] == b:
                    x = alpha[i + 1]
                else:
                    lock_A = 1
                    x = 1
                    last_1_a = i + 1

            print("Alice send:   ", x)
            await self.queue.put(x)
            await asyncio.sleep(0)

        if self.n % 2 == 0:
            b = await self.queue.get()
            print("Alice receive:", b, "\n")
            if b == 1:
                last_1_b = self.n

        print("Alice send lock_A:   ", lock_A)
        await self.queue.put(lock_A)
        await asyncio.sleep(0)

        lock_B = await self.queue.get()
        print("Alice receive lock_B:", lock_B)

        i_A = last_1_a - 1 if lock_A == 1 else self.n
        i_B = last_1_b - 1 if lock_B == 1 else self.n

        index = min(i_A, i_B)
        print("\nAlice thinks that index is:", index)

    async def Bob(self, beta):
        lock_B = 0
        last_1_a = 0
        last_1_b = 0

        for i in range(1, self.n, 2):
            a = await self.queue.get()
            print("Bob receive:  ", a)
            if a == 1:
                last_1_a = i

            if lock_B == 1:
                x = 0
            else:
                if beta[i] == a:
                    x = beta[i + 1]
                else:
                    lock_B = 1
                    x = 1
                    last_1_b = i + 1

            print("Bob send:     ", x)
            await self.queue.put(x)
            await asyncio.sleep(0)

        if self.n % 2 == 1:
            a = await self.queue.get()
            print("Bob receive:  ", a, "\n")
            if a == 1:
                last_1_a = self.n

        lock_A = await self.queue.get()
        print("Bob receive lock_A:  ", lock_A)

        print("Bob send lock_B:     ", lock_B)
        await self.queue.put(lock_B)
        await asyncio.sleep(0)

        i_A = last_1_a - 1 if lock_A == 1 else self.n
        i_B = last_1_b - 1 if lock_B == 1 else self.n

        index = min(i_A, i_B)
        print("Bob thinks that index is:  ", index)


def error_detect(s):
    if (len(s) & (len(s) - 1)) or len(s) < 2 or not all(c in "01" for c in s):
        return True
    else:
        if all(c == "0" for c in s):
            print("Your function is identically equal to 0")
            return True

        if all(c == "1" for c in s):
            print("Your function is identically equal to 1")
            return True

        return False


def get_input():
    s = input("\nEnter a column of function values: ")
    while error_detect(s):
        s = input("Enter exactly 2^n zeros and ones:  ")

    return s


async def launch():
    values = [int(c) for c in get_input()]
    n = int(math.log(len(values), 2))
    table = [*([*map(lambda input: [*input], product({0, 1}, repeat=n))])]

    print("\n Truth table:\n")
    for i in range(len(table)):
        print("", *table[i], "|", values[i])

    B0 = []
    B1 = []
    for i in range(len(table)):
        if values[i] == 0:
            B0.append(table[i])
        else:
            B1.append(table[i])

    print("\nB0:")
    for line in B0:
        print(*line)
    print("\nB1:")
    for line in B1:
        print(*line)
    print()

    for i in range(len(B0)):
        for j in range(len(B1)):
            diff = sum([abs(B0[i][k] - B1[j][k]) for k in range(n)])
            if diff == 1:
                alpha = B1[j]
                beta = B0[i]
                break
        if diff == 1:
            break

    print("Alice:", *alpha)
    print("Bob:  ", *beta)

    protocols = {"Simple": Simple, "Trivial": Trivial}

    for protocol in protocols:
        print("\n\nProtocol ", protocol, ":\n", sep="")
        protocol = protocols[protocol](n)

        f1 = loop.create_task(protocol.Alice(["a"] + alpha))
        f2 = loop.create_task(protocol.Bob(["b"] + beta))
        await asyncio.wait([f1, f2])


if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(launch())
    loop.close()
