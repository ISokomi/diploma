import asyncio, math           # Библиотека для асинхронного программирования и библиотека с математическими функциями
from itertools import product  # Функция для получения декартового произведения множества (0, 1) для таблицы истинности


class Trivial: # Класс, реализующий протокол Trivial
    def __init__(self, n):
        self.n = n
        self.queue = asyncio.Queue(1)

    async def Alice(self, alpha):
        for i in range(1, self.n + 1):
            x = alpha[i]
            print("Alice sends:   ", x)
            await self.queue.put(x)
            await asyncio.sleep(0)

        index = ""
        for i in range(int(math.log(self.n - 1, 2)) + 1):
            bit_of_index = await self.queue.get()
            print("Alice receives index:", bit_of_index)
            index += bit_of_index

        index = int(index, 2) + 1
        print("\nAlice thinks that index is:", index)
        return index

    async def Bob(self, beta):
        for i in range(1, self.n + 1):
            a = await self.queue.get()
            print("Bob receives:  ", a)

            if beta[i] != a:
                index = i

        print()
        index_bit_len = int(math.log(self.n - 1, 2)) + 1
        d = bin(index - 1)[2:].zfill(index_bit_len)
        for i in range(index_bit_len):
            print("Bob sends index:     ", d[i])
            await self.queue.put(d[i])
            await asyncio.sleep(0)

        print("Bob thinks that index is:  ", index)
        return index


class Simple: # Класс, реализующий протокол Simple
    def __init__(self, n):
        self.n = n
        self.queue = asyncio.Queue(1)

    async def Alice(self, alpha):
        lock_A = 0
        last_1_a = 0
        last_1_b = 0

        x = alpha[1]
        print("Alice sends:   ", x)
        await self.queue.put(x)
        await asyncio.sleep(0)

        for i in range(2, self.n, 2):
            b = await self.queue.get()
            print("Alice receives:", b)
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

            print("Alice sends:   ", x)
            await self.queue.put(x)
            await asyncio.sleep(0)

        if self.n % 2 == 0:
            b = await self.queue.get()
            print("Alice receives:", b, "\n")
            if b == 1:
                last_1_b = self.n

        print("Alice sends lock_A:   ", lock_A)
        await self.queue.put(lock_A)
        await asyncio.sleep(0)

        lock_B = await self.queue.get()
        print("Alice receives lock_B:", lock_B)

        i_A = last_1_a - 1 if lock_A == 1 else self.n
        i_B = last_1_b - 1 if lock_B == 1 else self.n

        index = min(i_A, i_B)
        print("\nAlice thinks that index is:", index)
        return index

    async def Bob(self, beta):
        lock_B = 0
        last_1_a = 0
        last_1_b = 0

        for i in range(1, self.n, 2):
            a = await self.queue.get()
            print("Bob receives:  ", a)
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

            print("Bob sends:     ", x)
            await self.queue.put(x)
            await asyncio.sleep(0)

        if self.n % 2 == 1:
            a = await self.queue.get()
            print("Bob receives:  ", a, "\n")
            if a == 1:
                last_1_a = self.n

        lock_A = await self.queue.get()
        print("Bob receives lock_A:  ", lock_A)

        print("Bob sends lock_B:     ", lock_B)
        await self.queue.put(lock_B)
        await asyncio.sleep(0)

        i_A = last_1_a - 1 if lock_A == 1 else self.n
        i_B = last_1_b - 1 if lock_B == 1 else self.n

        index = min(i_A, i_B)
        print("Bob thinks that index is:  ", index)
        return index


class Ham3: # Класс, реализующий протокол Ham3
    def __init__(self, n):
        self.n = n
        self.queue = asyncio.Queue(1)

        self.r = int(math.log(self.n, 2))
        self.s = self.n - 2**self.r

        self.C_n = []

        # Получение таблиц истинности
        table1 = [*([*map(lambda input: [*input], product({0, 1},
                                     repeat=2**(self.r-1)))])]
        table2 = [*([*map(lambda input: [*input], product({0, 1},
                                     repeat=self.r-1))])]
        table3 = [*([*map(lambda input: [*input], product({0, 1},
                                     repeat=2**(self.r - 1) - (self.r - 1)))])]
        self.label = [''.join(map(str, t)) for t in table3]

        for i in range(len(table1)):
            flag = 1
            for j in range(self.r - 1):
                sum = 0
                for k in range(2**(self.r - 1)):
                    sum += table1[i][k] * table2[k][j]
                if sum % 2:
                    flag = 0
                    break
            if flag:
                self.C_n.append(table1[i])

    def sph(self, x):
        for i in range(len(self.C_n)):
            c = self.C_n[i]
            diff = sum([abs(x[k] - c[k]) for k in range(2**(self.r - 1))])
            if diff == 1:
                return self.label[i]

    def ind(self, x):
        c = self.C_n[int(self.sph(x), 2)]
        for i in range(2**(self.r - 1)):
            if x[i] != c[i]:
                return i + 1

    async def Alice(self, alpha):
        X0 = alpha[1 : self.s + 1]
        X1 = alpha[self.s + 1 : self.s + 2**(self.r - 1) + 1]
        X2 = alpha[self.s + 2**(self.r - 1) + 1 :]

        print("Sending X0:")
        for i in range(self.s):
            x = X0[i]
            print("Alice sends:    ", x)
            await self.queue.put(x)
            await asyncio.sleep(0)

        print("\nSending sph(X1):")
        sphX1 = self.sph(X1)
        for i in range(2**(self.r - 1) - (self.r - 1)):
            x = sphX1[i]
            print("Alice sends:    ", x)
            await self.queue.put(x)
            await asyncio.sleep(0)

        bit1 = await self.queue.get()
        print("Alice receives bit1:  ", bit1)

        if bit1 == 0:
            index = 0
            for i in range(2**(self.r - 1)):
                b = await self.queue.get()
                print("Alice receives: ", b)

                if X2[i] != b:
                    index = i + 1
            print()

            if index != 0:
                bit2 = 0
                print("Alice sends bit2:   ", bit2)
                await self.queue.put(bit2)
                await asyncio.sleep(0)

                d2 = bin(index - 1)[2:].zfill(self.r - 1)
                for i in range(self.r - 1):
                    print("Alice sends index:  ", d2[i])
                    await self.queue.put(d2[i])
                    await asyncio.sleep(0)
                res = self.s + 2**(self.r - 1) + index
            elif index == 0:
                bit2 = 1
                print("Alice sends bit2:   ", bit2)
                await self.queue.put(bit2)
                await asyncio.sleep(0)

                index = self.ind(X1)
                d1 = bin(index - 1)[2:].zfill(self.r - 1)
                for i in range(self.r - 1):
                    print("Alice sends index:  ", d1[i])
                    await self.queue.put(d1[i])
                    await asyncio.sleep(0)
                res = self.s + index
        elif bit1 == 1:
            bit3 = await self.queue.get()
            print("Alice receives bit3:  ", bit3)

            if bit3 == 0:
                d0 = ""
                for i in range(int(math.log(self.s, 2)) + 1):
                    bit_of_index = await self.queue.get()
                    print("Alice receives index: ", bit_of_index)
                    d0 += bit_of_index
                d0 = int(d0, 2) + 1
                res = d0
                print()
            elif bit3 == 1:
                index = 0
                for i in range(2**(self.r - 1)):
                    b = await self.queue.get()
                    print("Alice receives: ", b)

                    if X1[i] != b:
                        index = i + 1
                print()

                d1 = bin(index - 1)[2:].zfill(self.r - 1)
                for i in range(self.r - 1):
                    print("Alice sends index: ", d1[i])
                    await self.queue.put(d1[i])
                    await asyncio.sleep(0)
                res = self.s + index

        print("Alice thinks that index is:", res)
        return res

    async def Bob(self, beta):
        Y0 = beta[1 : self.s + 1]
        Y1 = beta[self.s + 1 : self.s + 2**(self.r - 1) + 1]
        Y2 = beta[self.s + 2**(self.r - 1) + 1 :]

        index = 0
        for i in range(self.s):
            a = await self.queue.get()
            print("Bob receives:   ", a)

            if Y0[i] != a:
                index = i + 1

        sphY1 = self.sph(Y1)
        sphX1 = ""
        for i in range(2**(self.r - 1) - (self.r - 1)):
            a = await self.queue.get()
            print("Bob receives:   ", a)
            sphX1 += a
        print()

        if index == 0 and sphX1 == sphY1:
            bit1 = 0
            print("Bob sends bit1:       ", bit1)
            await self.queue.put(bit1)
            await asyncio.sleep(0)

            print("\nSending Y2:")
            for i in range(2**(self.r - 1)):
                x = Y2[i]
                print("Bob sends:      ", x)
                await self.queue.put(x)
                await asyncio.sleep(0)

            bit2 = await self.queue.get()
            print("Bob receives bit2:  ", bit2)

            if bit2 == 0:
                d2 = ""
                for i in range(self.r - 1):
                    bit_of_index = await self.queue.get()
                    print("Bob receives index: ", bit_of_index)
                    d2 += bit_of_index
                d2 = int(d2, 2) + 1
                res = self.s + 2**(self.r - 1) + d2
            elif bit2 == 1:
                d1 = ""
                for i in range(self.r - 1):
                    bit_of_index = await self.queue.get()
                    print("Bob receives index: ", bit_of_index)
                    d1 += bit_of_index
                d1 = int(d1, 2) + 1
                res = self.s + d1
            print()
        elif index != 0:
            bit1 = 1
            print("Bob sends bit1:       ", bit1)
            await self.queue.put(bit1)
            bit3 = 0
            print("Bob sends bit3:       ", bit3)
            await self.queue.put(bit3)
            await asyncio.sleep(0)

            index_bit_len = int(math.log(self.s, 2)) + 1
            d0 = bin(index - 1)[2:].zfill(index_bit_len)
            for i in range(index_bit_len):
                print("Bob sends index:      ", d0[i])
                await self.queue.put(d0[i])
                await asyncio.sleep(0)
            res = index
        elif index == 0 and sphX1 != sphY1:
            bit1 = 1
            print("Bob sends bit1:       ", bit1)
            await self.queue.put(bit1)
            bit3 = 1
            print("Bob sends bit3:       ", bit3)
            await self.queue.put(bit3)
            await asyncio.sleep(0)

            print("\nSending Y1:")
            for i in range(2**(self.r - 1)):
                x = Y1[i]
                print("Bob sends:      ", x)
                await self.queue.put(x)
                await asyncio.sleep(0)

            d1 = ""
            for i in range(self.r - 1):
                bit_of_index = await self.queue.get()
                print("Bob receives index:", bit_of_index)
                d1 += bit_of_index
            d1 = int(d1, 2) + 1
            res = self.s + d1
            print()

        print("Bob thinks that index is:  ", res)
        return res


def error_detect(s): # Функция для проверки корректности входных данных
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


def get_input(): # Функция, проверяющая входные данные
    s = input("\nEnter a column of function values: ")
    while error_detect(s):
        s = input("Enter exactly 2^n zeros and ones:  ")

    return s


async def launch(): # Функция, запускающая протоколы
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

    protocols = {"Trivial" : Trivial, "Simple" : Simple, "Ham3" : Ham3}

    for protocol in protocols:
        print("\n\nProtocol ", protocol, ":\n", sep="")
        protocol = protocols[protocol](n)

        f1 = loop.create_task(protocol.Alice(["a"] + alpha))
        f2 = loop.create_task(protocol.Bob(["b"] + beta))
        await asyncio.wait([f1, f2])

    # Тестирование
    test_mode = 0
    if test_mode:
        flag = 0
        for i in range(len(table)):
            for j in range(len(table)):
                diff = 0
                index = 0
                for k in range(n):
                    di = abs(table[i][k] - table[j][k])
                    if di == 1:
                        index = k + 1
                    diff += di
                if diff == 1:
                    alpha = table[j]
                    beta = table[i]

                    for protocol in protocols:
                        protocol = protocols[protocol](n)

                        f1 = loop.create_task(protocol.Alice(["a"] + alpha))
                        f2 = loop.create_task(protocol.Bob(["b"] + beta))
                        await asyncio.wait([f1, f2])

                        f1_res = f1.result()
                        f2_res = f2.result()
                        if f1_res != f2_res or f1_res != index:
                            print(alpha, "\n", beta)
                            print(f1_res, f2_res, index)
                            flag = 1
        if not flag:
            print("\nAll tests have been passed!")


if __name__ == "__main__": # Запуск главной функции launch()
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(launch())
    loop.close()