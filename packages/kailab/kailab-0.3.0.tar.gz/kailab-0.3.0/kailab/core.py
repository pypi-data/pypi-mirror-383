

def basiean():
    return '''# Import libraries
    from sklearn.model_selection import train_test_split
    from sklearn.feature_extraction.text import CountVectorizer
    from sklearn.naive_bayes import MultinomialNB
    from sklearn.metrics import accuracy_score, confusion_matrix, classification_report

    # Sample dataset
    texts = [
        "I love this product, it’s amazing!",
        "This is the best movie I have seen.",
        "I hate this item, it’s terrible.",
        "Awful experience, never buying again.",
        "Great quality and very useful.",
        "Worst product ever, do not buy!"
    ]

    # Labels: 1 = positive, 0 = negative
    labels = [1, 1, 0, 0, 1, 0]

    # Step 1: Convert text to feature vectors
    vectorizer = CountVectorizer()
    X = vectorizer.fit_transform(texts)

    # Step 2: Split data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(X, labels, test_size=0.3, random_state=42)

    # Step 3: Train Naive Bayes classifier
    model = MultinomialNB()
    model.fit(X_train, y_train)

    # Step 4: Predict
    y_pred = model.predict(X_test)

    # Step 5: Evaluate
    print("Accuracy:", accuracy_score(y_test, y_pred))
    print("\nConfusion Matrix:\n", confusion_matrix(y_test, y_pred))
    print("\nClassification Report:\n", classification_report(y_test, y_pred))

    # Test with new data
    sample = ["This product is good", "I dislike this movie"]
    sample_features = vectorizer.transform(sample)
    print("\nPredictions:", model.predict(sample_features))
    '''

def cartpole():
    return '''import gymnasium as gym
    import numpy as np

    env = gym.make("CartPole-v1")

    # Create Q-table
    state_bins = [6, 12, 6, 12]
    q_table = np.zeros(state_bins + [env.action_space.n])

    # Hyperparameters
    alpha = 0.1
    gamma = 0.99
    epsilon = 1.0
    epsilon_decay = 0.995
    episodes = 1000

    # Helper to discretize continuous state
    def discretize_state(state):
        cart_pos, cart_vel, pole_angle, pole_vel = state
        bins = [
            np.linspace(-2.4, 2.4, state_bins[0]),
            np.linspace(-3.0, 3.0, state_bins[1]),
            np.linspace(-0.21, 0.21, state_bins[2]),
            np.linspace(-2.0, 2.0, state_bins[3])
        ]
        indices = [np.digitize(s, b) for s, b in zip(state, bins)]
        # Clip to prevent out-of-range errors
        indices = [min(max(0, i), n - 1) for i, n in zip(indices, state_bins)]
        return tuple(indices)

    # Training loop
    for ep in range(episodes):
        state, _ = env.reset()
        state = discretize_state(state)
        done = False
        total_reward = 0

        while not done:
            # ε-greedy action
            if np.random.random() < epsilon:
                action = env.action_space.sample()
            else:
                action = np.argmax(q_table[state])

            next_state_raw, reward, terminated, truncated, _ = env.step(action)
            done = terminated or truncated
            next_state = discretize_state(next_state_raw)

            # Q-learning update
            q_table[state + (action,)] += alpha * (
                reward + gamma * np.max(q_table[next_state]) - q_table[state + (action,)]
            )

            state = next_state
            total_reward += reward

        epsilon = max(0.01, epsilon * epsilon_decay)
        if ep % 100 == 0:
            print(f"Episode {ep}, Reward: {total_reward}, Epsilon: {epsilon:.3f}")

    env.close()
    print("Training finished ")
'''

def basieanTamil():
    return '''from sklearn.model_selection import train_test_split
    from sklearn.feature_extraction.text import CountVectorizer
    from sklearn.naive_bayes import MultinomialNB
    from sklearn.metrics import accuracy_score, classification_report

    # Sample Tanglish dataset (texts, sentiment labels)
    texts = [
        "Naan indha product-a virumbugiren",      # Good
        "Indha padam sarasari dhaan",             # Neutral
        "Indha anubavam mosamana",                # Bad
        "Sirandha dharam matrum payanulla",       # Good
        "Miga mosamana product",                  # Bad
        "Idhu sarasari nilai"                     # Neutral
    ]

    # Labels: 2 = Good, 1 = Neutral, 0 = Bad
    labels = [2, 1, 0, 2, 0, 1]

    # Step 1: Convert text to feature vectors
    vectorizer = CountVectorizer()
    X = vectorizer.fit_transform(texts)

    # Step 2: Split dataset
    X_train, X_test, y_train, y_test = train_test_split(X, labels, test_size=0.3, random_state=42)

    # Step 3: Train Naive Bayes classifier
    model = MultinomialNB()
    model.fit(X_train, y_train)

    # Step 4: Evaluate
    y_pred = model.predict(X_test)
    print("Accuracy:", accuracy_score(y_test, y_pred))
    print("\nClassification Report:\n", classification_report(y_test, y_pred))

    # Step 5: Test new Tanglish sentences
    samples = [
        "Indha unavu arumai",     # Good
        "Sari dhaan",             # Neutral
        "Miga mosamana service"   # Bad
    ]
    sample_features = vectorizer.transform(samples)
    predictions = model.predict(sample_features)

    # Map numeric labels back to text
    sentiment_map = {2: "Good", 1: "Neutral", 0: "Bad"}
    for text, label in zip(samples, predictions):
        print(f"Sentence: {text} --> Sentiment: {sentiment_map[label]}")
    '''

def basieanImg():
    return '''import os
    import numpy as np
    from PIL import Image
    from sklearn.model_selection import train_test_split
    from sklearn.naive_bayes import GaussianNB
    from sklearn.metrics import accuracy_score, classification_report

    # Step 1: Dataset path and classes
    dataset_path = "flowers_dataset"
    classes = os.listdir(dataset_path)  # ['rose', 'sunflower', 'tulip']

    X = []
    y = []

    # Step 2: Load images and labels
    for idx, cls in enumerate(classes):
        folder = os.path.join(dataset_path, cls)
        for filename in os.listdir(folder):
            if filename.endswith(".jpg") or filename.endswith(".png"):
                img_path = os.path.join(folder, filename)
                img = Image.open(img_path).convert('L')  # grayscale
                img = img.resize((32, 32))               # resize small
                data = np.array(img).flatten()           # flatten to 1D
                X.append(data)
                y.append(idx)                            # numeric label

    X = np.array(X)
    y = np.array(y)

    # Step 3: Split into train/test
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

    # Step 4: Train Gaussian Naive Bayes
    model = GaussianNB()
    model.fit(X_train, y_train)

    # Step 5: Predict and Evaluate
    y_pred = model.predict(X_test)
    print("Accuracy:", accuracy_score(y_test, y_pred))
    print("\nClassification Report:\n", classification_report(y_test, y_pred, target_names=classes))

    # Step 6: Test a new image
    test_img_path = "test_flower.jpg"
    img = Image.open(test_img_path).convert('L')
    img = img.resize((32, 32))
    data = np.array(img).flatten().reshape(1, -1)

    pred = model.predict(data)
    print(f"The predicted flower is: {classes[pred[0]]}")
    '''

def astar():
    return '''
    from heapq import heappush,heappop

    class Node:

        def __init__(self,name,parent = None ,g=0,h=0):
            self.name = name
            self.parent = parent
            self.g=g
            self.h=h
            self.f=g+h

        def __lt__(self,other):
            return self.f<other.f
        

    def Astar(graph,start,goal,herustic):

        openList = []
        closedList = set()

        heappush(openList,Node(start,None,0,herustic[start]))

        while openList:

            current = heappop(openList)

            if current.name == goal:
                path = []
                print("cost : ",current.g)
                while current:
                    path.append(current.name)
                    current = current.parent

                return path[::-1]
            
            closedList.add(current.name)

            for neighbour,cost in graph[current.name].items():

                if neighbour in closedList: continue

                g = current.g+cost
                h = herustic.get(neighbour,0)

                heappush(openList,Node(neighbour,current,g,h))

        return None

    n = int(input("Enter no of nodes :"))
    m = int(input("Enter no of edges :"))
    print("Enter nodes names : ")
    nodes = input().split()

    graph = {}
    for i in nodes:
        graph[i] = {}

    print("Enter edges as src des cost :\n")
    for _ in range(m):
        src,des,cost = input().split()
        graph[src][des]=int(cost)


    herustic = {}
    for node in nodes:
        herustic[node] = int(input(f"Enter herustic for {node}:"))

    st = input("Enter start node :").strip()
    end = input("enter end node :").strip()

    path = Astar(graph,st,end,herustic)

    if path:
        print("path :","->".join(path))
    else:
        print("No path")'''


def simAn():
    return '''import math
    import random

    # Objective function
    def f(x):
        return x**2 + 10 * math.sin(x)

    # Simulated Annealing
    def simulated_annealing(f, x0, T=1000, alpha=0.9, max_iter=1000):
        x = x0
        fx = f(x)

        for i in range(max_iter):
            # Generate new candidate nearby
            x_new = x + random.uniform(-1, 1)
            fx_new = f(x_new)

            # Accept new candidate if better, or with some probability if worse
            if fx_new < fx or random.random() < math.exp(-(fx_new - fx) / T):
                x = x_new
                fx = fx_new

            # Cool down temperature
            T *= alpha

        return x, fx

    # Run Simulated Annealing
    x0 = random.uniform(-10, 10)
    best_x, best_fx = simulated_annealing(f, x0)
    print("Minimum x:", best_x)
    print("Minimum f(x):", best_fx)
    '''

def crypt():
    return '''from itertools import permutations

    w1 = input("Enter word 1 :")
    w2 = input("Enter word 2 :")
    R = input("Enter result : ")

    uniqueLetters = set(w1+w2+R)
    uniqueLetters = list(uniqueLetters)

    if(len(uniqueLetters) > 10):
        print("More than 10!")
        exit()

    for perm in permutations(range(10),len(uniqueLetters)):
        
        mappings = dict(zip(uniqueLetters,perm))

        if any(mappings[word[0]]==0 for word in [w1,w2,R]):
            continue

        lv1 = int(''.join(str(mappings[c]) for c in w1))
        lv2 = int(''.join(str(mappings[c]) for c in w2) )   
        rv = int(''.join(str(mappings[c]) for c in R))

        if (lv1+lv2)==rv:
            print("Solution found!")
            print(f"Mappings : {mappings}")
            print(f"{lv1} + {lv2} = {lv1+lv2}")
            break
    else:
        print("Solution not found")


    '''

def tictac():
    return '''import math

    # ---------- Display Board ----------
    def print_board(board):
        print("\n")
        for i in range(3):
            print(board[i][0], "|", board[i][1], "|", board[i][2])
            if i != 2:
                print("--+---+--")
        print("\n")

    # ---------- Check for Winner ----------
    def check_winner(board):
        # Rows, columns, diagonals
        for i in range(3):
            if board[i][0] == board[i][1] == board[i][2] != ' ':
                return board[i][0]
            if board[0][i] == board[1][i] == board[2][i] != ' ':
                return board[0][i]

        if board[0][0] == board[1][1] == board[2][2] != ' ':
            return board[0][0]
        if board[0][2] == board[1][1] == board[2][0] != ' ':
            return board[0][2]

        return None

    # ---------- Check if Moves are Left ----------
    def moves_left(board):
        for row in board:
            if ' ' in row:
                return True
        return False

    # ---------- Minimax Algorithm ----------
    def minimax(board, depth, is_maximizing):
        winner = check_winner(board)
        if winner == 'X':
            return 10 - depth   # prefer faster wins
        elif winner == 'O':
            return depth - 10   # prefer slower losses
        elif not moves_left(board):
            return 0  # draw

        if is_maximizing:
            best = -math.inf
            for i in range(3):
                for j in range(3):
                    if board[i][j] == ' ':
                        board[i][j] = 'X'
                        value = minimax(board, depth + 1, False)
                        board[i][j] = ' '
                        best = max(best, value)
            return best
        else:
            best = math.inf
            for i in range(3):
                for j in range(3):
                    if board[i][j] == ' ':
                        board[i][j] = 'O'
                        value = minimax(board, depth + 1, True)
                        board[i][j] = ' '
                        best = min(best, value)
            return best

    # ---------- Find Best Move for AI ----------
    def find_best_move(board):
        best_value = -math.inf
        best_move = (-1, -1)

        for i in range(3):
            for j in range(3):
                if board[i][j] == ' ':
                    board[i][j] = 'X'
                    move_value = minimax(board, 0, False)
                    board[i][j] = ' '
                    if move_value > best_value:
                        best_value = move_value
                        best_move = (i, j)

        return best_move

    # ---------- Main Game Loop ----------
    def play_game():
        board = [[' ' for _ in range(3)] for _ in range(3)]

        print("You are O, AI is X")
        print_board(board)

        while True:
            # Player move
            while True: 
                move = input("Enter your move (row and column 0-2 separated by space): ")
                r, c = map(int, move.split())
                if board[r][c] == ' ':
                    board[r][c] = 'O'
                    break
                else:
                    print("That spot is taken. Try again.")

            print_board(board)


            if check_winner(board) == 'O':
                print("🎉 You win!")
                break

            if not moves_left(board):
                print("It's a draw!")
                break

            # AI move
            print("AI is making a move...")
            ai_move = find_best_move(board)
            board[ai_move[0]][ai_move[1]] = 'X'


            print_board(board)

            if check_winner(board) == 'X':
                print("💻 AI wins!")
                break
            
            if not moves_left(board):
                print("It's a draw!")
                break

    play_game()
    '''

def NQGA():
    
    return '''import random

    n = int(input("Enter no of Queens : "))

    if n<3:
        print("Solution can't be found!")

    def fitness(board):
        conflict = 0 
        for i in range(n):
            for j in range(i+1,n):
                if board[i]==board[j] or abs(board[i]-board[j]) == abs(i-j):
                    conflict+=1

        return conflict

    def crossover(p1,p2):
        point = random.randint(0,n-1)
        child = p1[:point]+p2[point:]
        return child

    def mutate(board):

        newBoard = board
        col = random.randint(0,n-1)
        newBoard[col] = random.randint(0,n-1)

        return newBoard

    MaxPop = 100
    mRate = 0.3
    MaxGen = 1000

    population  = [[random.randint(0,n-1) for _ in range(n)] for _ in range(MaxPop)]

    for generation in range(MaxGen):

        population.sort(key=fitness)
        best = population[0]
        
        bestFit = fitness(best)

        print(f"Generation {generation} | fitness : {bestFit} | board : {best}")

        if(bestFit == 0):
            print("solution found! : ",best)

            for i in range(n):
                for j in range(n):
                    if best[i]==j:
                        print('Q',end=" ")
                    else:
                        print('.',end=" ")
                print()
            break

        parents= population[:20]

        new_population = []
        for _ in range(MaxPop):

            #p1 = random.choice(parents)
            p2 = random.choice(parents)
            p1 = random.choices(parents,k=5)
            p1.sort(key=fitness)
            p1 = p1[0]

            child = crossover(p1,p2)

            if random.random() < mRate:
                child = mutate(child)

            new_population.append(child)

        population = new_population

    else:
        print("No slution found!")


    '''

def NQHC():
    return '''import random

    n = int(input("Enter number of Queens: "))

    # ---------- Calculate number of conflicts ----------
    def fitness(board):
        conflicts = 0
        for i in range(n):
            for j in range(i + 1, n):
                if board[i] == board[j] or abs(board[i] - board[j]) == abs(i - j):
                    conflicts += 1
        return conflicts

    # ---------- Generate neighbors ----------
    def get_neighbors(board):
        neighbors = []
        for col in range(n):
            for row in range(n):
                if row != board[col]:  # move queen to another row
                    new_board = board[:]
                    new_board[col] = row
                    neighbors.append(new_board)
        return neighbors

    # ---------- Hill Climbing Algorithm ----------
    def hill_climbing():
        # Start with a random board
        board = [random.randint(0, n-1) for _ in range(n)]
        
        steps = 0
        while True:
            current_fitness = fitness(board)
            
            if current_fitness == 0:
                return board, steps
            
            neighbors = get_neighbors(board)
            # Choose the neighbor with minimum conflicts
            next_board = min(neighbors, key=fitness)
            next_fitness = fitness(next_board)
            
            # If no improvement, restart
            if next_fitness >= current_fitness:
                board = [random.randint(0, n-1) for _ in range(n)]
                steps += 1
                continue
            
            board = next_board
            steps += 1

    # ---------- Run ----------
    solution, steps = hill_climbing()
    print(f"Solution found in {steps} steps:")
    print(solution)

    # Optional: print board nicely
    for row in range(n):
        line = ""
        for col in range(n):
            if solution[col] == row:
                line += "Q "
            else:
                line += ". "
        print(line)
    '''

def GAFX():
    return '''import random

    # Objective function
    def f(x):
        return x**2

    # Generate initial population
    def generate_population(size, x_min, x_max):
        return [random.uniform(x_min, x_max) for _ in range(size)]

    # Selection: Roulette Wheel
    def selection(population, fitness):
        total_fitness = sum(fitness)
        pick = random.uniform(0, total_fitness)
        current = 0
        for ind, fit in zip(population, fitness):
            current += fit
            if current > pick:
                return ind

    # Crossover: simple average
    def crossover(parent1, parent2):
        return (parent1 + parent2) / 2

    # Mutation: small random change
    def mutate(x, mutation_rate=0.1):
        if random.random() < mutation_rate:
            x += random.uniform(-1, 1)
        return x

    # Genetic Algorithm
    def genetic_algorithm(pop_size=10, generations=50, x_min=-10, x_max=10):
        # Step 1: initialize
        population = generate_population(pop_size, x_min, x_max)

        for gen in range(generations):
            # Step 2: evaluate fitness (minimization -> higher fitness = smaller value)
            fitness = [1/(1+f(x)) for x in population]

            new_population = []
            for _ in range(pop_size):
                # Step 3: select two parents
                p1 = selection(population, fitness)
                p2 = selection(population, fitness)
                # Step 4: crossover
                child = crossover(p1, p2)
                # Step 5: mutate
                child = mutate(child)
                # Add to new population
                new_population.append(child)
            population = new_population

        # Return best solution
        best_x = min(population, key=f)
        return best_x, f(best_x)

    # Run GA
    best_x, best_val = genetic_algorithm()
    print("Best x:", best_x)
    print("f(x):", best_val)
    '''
def ucs():
    return '''from heapq import heappush, heappop

    class Node:
        def __init__(self, name, parent=None, cost=0):
            self.name = name
            self.parent = parent
            self.cost = cost  # Total path cost from start to this node

        def __lt__(self, other):
            return self.cost < other.cost


    def uniform_cost_search(graph, start, goal):
        open_list = []
        closed_list = set()

        heappush(open_list, Node(start, None, 0))

        while open_list:
            current = heappop(open_list)

            # Goal test
            if current.name == goal:
                path = []
                total_cost = current.cost
                while current:
                    path.append(current.name)
                    current = current.parent
                return path[::-1], total_cost

            if current.name in closed_list:
                continue

            closed_list.add(current.name)

            # Explore neighbors
            for neighbor, cost in graph[current.name].items():
                if neighbor not in closed_list:
                    new_cost = current.cost + cost
                    heappush(open_list, Node(neighbor, current, new_cost))

        return None, float('inf')


    # ----------- MAIN PROGRAM -----------
    n = int(input("Enter number of nodes: "))
    m = int(input("Enter number of edges: "))

    print("Enter node names:")
    nodes = input().split()

    graph = {i: {} for i in nodes}

    print("Enter edges as src dest cost:")
    for _ in range(m):
        src, dest, cost = input().split()
        graph[src][dest] = int(cost)

    start = input("Enter start node: ").strip()
    goal = input("Enter goal node: ").strip()

    path, cost = uniform_cost_search(graph, start, goal)

    if path:
        print("Path:", " -> ".join(path))
        print("Total cost:", cost)
    else:
        print("No path found.")
    '''

def wj():
    return '''from collections import deque

    # def water_jug_bfs(x, y, z):
    #     # To store visited states
    #     visited = set()
    #     # Queue will store tuples (jug1, jug2)
    #     queue = deque()
        
    #     # Start with both jugs empty
    #     queue.append((0, 0))
        
    #     while queue:
    #         a, b = queue.popleft()
            
    #         # If this state was already visited, skip
    #         if (a, b) in visited:
    #             continue
    #         visited.add((a, b))
            
    #         print(f"State: ({a}, {b})")
            
    #         # If we reach the target
    #         if a == z or b == z:
    #             print("\n✅ Goal reached!")
    #             return
            
    #         # Generate all possible next states
    #         next_states = [
    #             (x, b),          # Fill Jug1
    #             (a, y),          # Fill Jug2
    #             (0, b),          # Empty Jug1
    #             (a, 0),          # Empty Jug2
    #             (a - min(a, y - b), b + min(a, y - b)),  # Pour Jug1 → Jug2
    #             (a + min(b, x - a), b - min(b, x - a))   # Pour Jug2 → Jug1
    #         ]
            
    #         for state in next_states:
    #             if state not in visited:
    #                 queue.append(state)
        
    #     print("❌ No solution found!")



    def water_jug_bfs(x,y,z):

        visited = set()

        q = deque()

        q.append((0,0))

        while q:
            a,b = q.popleft()

            if (a,b) in visited:
                continue

            visited.add((a,b))

            print("State : ",a," ",b)

            if a==z or b==z:
                print("Goal reached!")
                break

            newStates = [
                (x,b),(a,y),(0,b),(a,0),(a-min(a,y-b),b+min(a,y-b)),(a+min(b,x-a),b-min(b,x-a))
            ]
            
            for s in newStates:
                if s not in visited:
                    q.append(s)
        else:
            print("Not possible")

    # ---- Run the code ----
    x = int(input("Enter capacity of Jug 1: "))
    y = int(input("Enter capacity of Jug 2: "))
    z = int(input("Enter target amount: "))

    water_jug_bfs(x, y, z)
    '''
def alphaBeta():
    return '''import math

    def alphabeta_tree(arr, depth, index, max_depth, alpha, beta, maximizingPlayer):
        """
        arr : list of leaf values (flattened tree)
        depth : current depth in the tree
        index : current index in array (used to traverse)
        max_depth : maximum depth of the tree
        alpha, beta : alpha-beta values
        maximizingPlayer : True if maximizing, False if minimizing
        """
        # If leaf node or reached max depth
        if depth == max_depth:
            return arr[index]

        # Number of children per node (binary tree example)
        num_children = 2
        start = index * num_children

        if maximizingPlayer:
            maxEval = -math.inf
            for i in range(num_children):
                eval = alphabeta_tree(arr, depth+1, start + i, max_depth, alpha, beta, False)
                maxEval = max(maxEval, eval)
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break  # Beta cut-off
            return maxEval
        else:
            minEval = math.inf
            for i in range(num_children):
                eval = alphabeta_tree(arr, depth+1, start + i, max_depth, alpha, beta, True)
                minEval = min(minEval, eval)
                beta = min(beta, eval)
                if beta <= alpha:
                    break  # Alpha cut-off
            return minEval

    # Example usage
    # Flattened binary tree leaf nodes
    # Depth = 3, so 2^3 = 8 leaf nodes
    leaves = [3, 5, 6, 9, 1, 2, 0, -1]
    max_depth = 3

    best_value = alphabeta_tree(leaves, 0, 0, max_depth, -math.inf, math.inf, True)
    print("Best value for maximizing player:", best_value)
    '''
def help():
    return ["basiean", "cartpole", "basieanTamil", "basieanImg","astar","simAn","crypt","tictac","NQGA","NQHC","GAFX","ucs","wj","alphaBeta"]