import os

def compare(file1:str, file2:str):
    with open(file1) as f1, open(file2) as f2:
        lines1 = f1.readlines()
        lines2 = f2.readlines()
        i = 0
        cnt = 0
        for a, b in zip(lines1, lines2):
            a = a.strip()
            b = b.strip()
            i += 1
            if abs(float(a) - float(b)) < 1e-5: continue
            print(f"Diff @ L{i}", a, b)
            cnt += 1
        print(f"Total {cnt} diffs")
        return cnt

if __name__ == "__main__":
    print("Testing...")
    print("2islands DistFlow")
    os.system('python main.py -g cases/2islands.xml -o test/2islands_d.out -m DistFlow')
    print("33base DistFlow")
    os.system('python main.py -g cases/33base.xml -o test/33base_d.out -m DistFlow')
    print("33base Newton")
    os.system('python main.py -g cases/33base.xml -o test/33base_n.out -m Newton')
    print("33mulg DistFlow")
    os.system('python main.py -g cases/33mulg.xml -o test/33mulg_d.out -m DistFlow -b 0 -e 86400 -s 3600')
    print("33pvwd DistFlow")
    os.system('python main.py -g cases/33pvwd.xml -o test/33pvwd_d.out -m DistFlow -b 0 -e 86400 -s 3600')
    print("33esss DistFlow")
    os.system('python main.py -g cases/33esss.xml -o test/33esss_d.out -m DistFlow -b 0 -e 86400 -s 3600')