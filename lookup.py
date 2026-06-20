import requests
import json
import time

BASE_URL = "https://api.tuforums.com"
count = 0
api_time = 0

def fetchapi(url):
    global count
    global api_time

    headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36 Edg/132.0.2957.140"
        }

    count += 1
    t0 = time.perf_counter()
    r = requests.get(url,timeout=30,headers=headers)
    api_time += time.perf_counter() - t0
    r.raise_for_status()

    return r.json()

def search(query):
    url = f"{BASE_URL}/v3/players/search?query={query}"
    print(url)
    data = fetchapi(url)
    return data.get("results", [])

def find_player(query, by="discord"):
    offset = 0
    limit = 100

    while True:
        url = (
            f"{BASE_URL}/v3/players/leaderboard"
            f"?query="
            f"&sortBy=rankedScore"
            f"&order=desc"
            f"&offset={offset}"
            f"&limit={limit}"
            f"&showBanned=hide"
        )

        print(url)
        data = fetchapi(url)
        results = data.get("results", [])
        if not results: return None

        for player in results:
            discord = player.get("discord")
            if (discord and discord.get("username") and discord["username"].lower() == query.lower()):
                return player
        offset += limit

def get_player(pid):
    url = f"{BASE_URL}/v3/players/{pid}"
    print(url)
    return fetchapi(url)

def get_country_rank(player):
    country = player["country"]
    score = player["rankedScore"]
    filters = {
        "country": country,
        "rankedScore": [
            score,
            999999999
        ]
    }

    url = (
        f"{BASE_URL}/v3/players/leaderboard"
        f"?query="
        f"&sortBy=rankedScore"
        f"&order=desc"
        f"&offset=0"
        f"&limit=1"
        f"&showBanned=hide"
        f"&filters={requests.utils.quote(json.dumps(filters))}"
    )

    print(url)
    data = fetchapi(url)
    return data["count"]

def details(player, country_rank):
    discord = player.get("discord")
    td = player.get("topDiff")
    print("\n" + "=" * 70)
    print(f"名称: {player.get('name')}")
    print(f"ID: {player.get('id')}")
    print(f"Discord: {discord.get('username') if discord else 'N/A'}")
    print(f"国家: {player.get('country')}")
    print()
    print(f"全球排名: {player.get('rankedScoreRank', 'N/A')}")
    print(f"国家排名: {country_rank}")
    print()
    print(f"排位分: {player.get('rankedScore')}")
    print(f"全局分: {player.get('generalScore')}")
    print(f"总分: {player.get('totalScoreV2')}")
    print(f"PP分: {player.get('ppScore')}")
    print(f"WF分: {player.get('wfScore')}")
    print(f"WFPP分: {player.get('wfPPScore')}")
    print(f"12K分: {player.get('score12K')}")
    print()
    print(f"平均XACC: {player.get('averageXacc') * 100}%")
    print(f"U级通关数: {player.get('universalPassCount')}")
    print(f"总通关数: {player.get('totalPasses')}")
    print(f"世界首通数: {player.get('worldsFirstCount')}")
    print(f"WFPP数: {player.get('worldsFirstPPCount')}")
    if td: print(f"最高通关难度: {td.get('name')} ({td.get('sortOrder')})")

def stats():
    global count, api_time
    print(f"used {count} requests, {api_time * 1000:.2f} ms")
    print("\n"+ "=" * 70)
    count = 0
    api_time = 0

def choose_player(results):
    if len(results) == 1: return results[0]

    print("\n找到多个玩家：\n")

    for idx, player in enumerate(results, start=1):
        print(f"[{idx}] {player['name']} (ID={player['id']}, Country={player['country']}, RankedScore={player['rankedScore']:.2f})")

    while True:
        try:
            choice = int(input("\n选择玩家： "))
            if 1 <= choice <= len(results):
                return results[choice - 1]
        except:
            pass

        print("选择无效。")

def run(player):
    details(player, get_country_rank(player))
    print()
    stats()

def main():
    print("=== TUF 玩家查询 ===")
    while True:
        print("\n选择搜索类型")
        print("1. 名称")
        print("2. Discord 用户名")
        print("3. 玩家 ID")
        print("q. 退出")

        mode = input("\n> ")

        player = None

        if mode == "1":
            name = input("玩家名：").strip()

            results = search(name)

            if not results:
                print("未找到玩家。")
                stats()
                continue

            player = choose_player(results)

            if "rankedScoreRank" not in player:
                player = get_player(player["id"])

            run(player)

        elif mode == "2":
            username = input("Discord 用户名：").strip()

            results = search(f"@{username}")

            if not results:
                print("未找到玩家。")
                stats()
                continue

            player = choose_player(results)

            if "rankedScoreRank" not in player:
                player = get_player(player["id"])

            run(player)

        elif mode == "3":
            pid = input("玩家 ID：").strip()

            try:
                player = get_player(pid)
            except:
                player = None

            if not player:
                print("未找到玩家。")
                stats()
                continue

            run(player)

        elif mode == "q":
            print("exit")
            break

        else:
            print("搜索类型无效。")


            
if __name__ == "__main__":
    main()
