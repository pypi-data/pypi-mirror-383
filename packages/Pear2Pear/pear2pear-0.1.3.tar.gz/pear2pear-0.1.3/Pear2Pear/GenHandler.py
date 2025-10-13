import pandas as pd
from .GenUtils import apply_patterns, getSignal
import numpy as np
import random
from copy import deepcopy
import pandas as pd
import numba as nb
import os
import multiprocess


def get_schema(collumns):
    return [
        collumns,
        range(0, 4),
        ['>', '<'],
        collumns,
        range(0,  4),
    ]

def generate_pattern(schema, PatternSettings):
    pattern = [np.random.choice(rule) for rule in schema]
    firstPattern = pattern[0]
    secondePattern = pattern[3]

    firstPatternDescriptor = dict(PatternSettings[firstPattern])
    secondPatternDescriptor = dict(PatternSettings[secondePattern])

    if (secondePattern not in firstPatternDescriptor["comparativeRange"]):
        secondePattern = deepcopy(firstPattern)
        secondPatternDescriptor = PatternSettings[secondePattern]
    
    if (firstPattern not in secondPatternDescriptor["comparativeRange"]):
        firstPattern = deepcopy(secondePattern)
        firstPatternDescriptor = PatternSettings[firstPattern]

    if firstPatternDescriptor["numberRange"]["hasRange"] and  np.random.rand() < 0.5:
        result = random.uniform(firstPatternDescriptor["numberRange"]["min"],firstPatternDescriptor["numberRange"]["max"])
        secondePattern = str(result)

    if secondePattern == "Low" and secondePattern == "High" and pattern[1] == pattern[4]:
        pattern[1] += 1
    if secondePattern == "High" and secondePattern == "Low" and pattern[1] == pattern[4]:
        pattern[1] += 1
    if secondePattern == secondePattern and pattern[1] == pattern[4]:
        pattern[1] += 1
    if (secondePattern == "Low" or secondePattern == "High" and pattern[1] == pattern[4]):
        pattern[1] += 1
    if (secondePattern == "Low" or secondePattern == "High" and pattern[1] == pattern[4]):
        pattern[1] += 1
    pattern[0] = firstPattern 
    pattern[3] = secondePattern
    return pattern

def generate_random_pattern(schema, PatternSettings):
    patternList = []
    nbPattern = random.randint(1, 4)
    
    for _ in range(2):
        fullPat = [generate_pattern(schema, PatternSettings) for _ in range(nbPattern)]
        patternList.append(fullPat)
    
    return patternList

@nb.njit()
def Process_Gain(start_rows: np.ndarray, formatted_candles: np.ndarray, multiplicator: int, processed_rows: np.ndarray, gain_index: int, flag_index: int, close_index: int, index_index : int, low_index: int, high_index: int):
    for start_row in start_rows:
        if start_row[index_index] in processed_rows:
            continue
        upstart_index: int = int(start_row[index_index])
        current_index: int = upstart_index
        next_row_index: int = int(current_index + 1)
        while next_row_index < len(formatted_candles):
            next_row = formatted_candles[next_row_index]
            if(next_row_index - current_index > 200):
                formatted_candles[upstart_index, gain_index] = -50
                break
            next_row_limit = next_row[low_index] if  multiplicator> 0 else next_row[high_index]
            pct_variation = ((next_row_limit - start_row[close_index]) / next_row_limit * 100) * multiplicator
            SLPct: int = -3
            if (pct_variation <= SLPct):
                formatted_candles[upstart_index, gain_index] = SLPct
                break
            if (multiplicator >= 0):
                if next_row[flag_index] == -1 or next_row[flag_index] == -2:
                    percentage_gain = ((next_row[close_index] - start_row[close_index]) / start_row[close_index]) * 100
                    formatted_candles[upstart_index, gain_index] = percentage_gain * multiplicator
                    break
                else:
                    processed_rows = np.append(processed_rows, next_row_index)
            else:
                if next_row[flag_index] == 1 or next_row[flag_index] == -3:
                    percentage_gain = ((next_row[close_index] - start_row[close_index]) / start_row[close_index]) * 100
                    formatted_candles[upstart_index, gain_index] = percentage_gain * multiplicator
                    break
                else:
                    processed_rows = np.append(processed_rows, next_row_index)
            next_row_index += 1


@nb.njit()
def Process_Wallet(npCopyData: np.ndarray, walletIndex: int, gains: np.ndarray, index_index : int):
    for dataElem in npCopyData:
        index: int = int(dataElem[index_index])
        row_index = index  # Extracting the index from the tuple
        if row_index < 1:
            prevValue = 1000
        else:
            prevValue = npCopyData[row_index - 1, walletIndex]
        gainValue = ((gains[row_index] / 100) * prevValue) 
        value = gainValue + prevValue 
        if (gainValue):
            value = value - (prevValue * (0.04 / 100))
        npCopyData[row_index, walletIndex] = value




def evaluate_fitness(pattern, financial_data, isBellow):
    if (pattern):
        combined_condition_up = getSignal(pattern[0])
        combined_condition_down = getSignal(pattern[1])

        signals_up = eval(combined_condition_up)
        signals_down = eval(combined_condition_down)

        copyData: pd.DataFrame = deepcopy(financial_data)
        copyData.loc[signals_down, "Gflag"] = -1
        copyData.loc[signals_up, "Gflag"] = 1
        if (isBellow):
            cond = ((financial_data["Gflag"] > 0) | (financial_data["Gflag"] < 0))
            copyData.loc[cond, "Gflag"] = financial_data.loc[cond, "Gflag"]
    else:
        copyData: pd.DataFrame = deepcopy(financial_data)

    copyData["gain"] = 0.0
    processed_rows = np.array([-1])
    copyData.reset_index(drop=True, inplace=True)
    copyData["wallet"] = 1000.0
    copyData["index"] = copyData.index.values * 1.0
    upstart_rows = copyData[copyData["Gflag"] == 1]
    downstart_rows = copyData[copyData["Gflag"] == -1]
    timeIn = 100 - ((len(financial_data) - (len(upstart_rows) + len(downstart_rows)) ) / len(financial_data) * 100)
    if (timeIn < 2.5):
        return 0
    gain_index = copyData.columns.tolist().index('gain')
    flag_index =copyData.columns.tolist().index('Gflag')
    close_index = copyData.columns.tolist().index('Close')
    low_index = copyData.columns.tolist().index('Low')
    high_index = copyData.columns.tolist().index('High')
    index_index = copyData.columns.tolist().index('index')
    numpyData = copyData.to_numpy()
    numpyUpStart = upstart_rows.to_numpy()
    numpyDownStart = downstart_rows.to_numpy()
    Process_Gain(numpyUpStart, numpyData, 1, processed_rows, gain_index, flag_index, close_index, index_index, low_index, high_index)
    Process_Gain(numpyDownStart, numpyData, -1, processed_rows, gain_index, flag_index, close_index, index_index, low_index, high_index)
    copyData["gain"] = numpyData[:, gain_index]
    profitable_trades =np.sum(copyData[copyData["gain"] > 0]["gain"])
    losing_trades = np.sum(-copyData[copyData["gain"] < 0]["gain"])
    profit_factor = profitable_trades / losing_trades
    return profit_factor

def elitism(population, fitness_values, elitism_num):
    elite_indices = np.argsort(fitness_values)[-elitism_num:]
    return [list(population[i]) for i in elite_indices]

def select_parents(population, fitness_values):
    tempPopulation = population.copy()
    tempFiteness = fitness_values.copy()
    selected_parents = []
    for _ in range(0, 2):
        total_fitness = np.sum(tempFiteness)
        selected_fitness = random.uniform(0, total_fitness)
        accumulated_fitness = 0
        for i, fitness in enumerate(tempFiteness):
            accumulated_fitness += fitness
            if accumulated_fitness >= selected_fitness:
                selected_parents.append(list(tempPopulation[i]))
                break
    return selected_parents

def reproduce(parent1, parent2):
    split_point = max(np.random.randint(min(len(parent1),len(parent2))),1)
    child1 = parent1[:split_point]  + parent2[split_point:]
    child2 = parent2[:split_point]  + parent1[split_point:]
    return child1, child2

def mutate(pattern, mutation_chance, refresh_chance, schema, nonComparablePattern):
    paternMut = np.random.randint(len(pattern))
    if np.random.rand() < refresh_chance:
        return generate_random_pattern(schema, nonComparablePattern)[0]
    elif np.random.rand() < mutation_chance:
        pattern[paternMut] = generate_random_pattern(schema, nonComparablePattern)[0][0]

    return pattern

def evaluate_fitness_wrapper(args):
    pattern, financial_data, isBellow = args
    fitness = evaluate_fitness(pattern, financial_data, isBellow)
    return fitness

def getPreGen(financial_data, population_size, mutation_chance, refresh_chance, population, schema, nonComparablePattern, isBellow):
    fitness_values = []
    
    eval_args = [(pattern, financial_data, isBellow) for pattern in population]

    with multiprocess.Pool(processes=min(10, len(population))) as pool:
        fitness_values = pool.map(evaluate_fitness_wrapper, eval_args)
    mean = np.mean(fitness_values)
    sorted_indices = np.argsort(fitness_values)[::-1]
    population = [population[i] for i in sorted_indices]
    fitness_values = [fitness_values[i] for i in sorted_indices]
    bestPop = population[0].copy()
    new_population = []
    while len(new_population) < population_size:
        parents = select_parents(population, fitness_values)
        children_up_1, children_up_2 = reproduce(parents[0][0], parents[1][0])
        children_down_1, children_down_2 = reproduce(parents[0][1], parents[1][1])
        new_population.append([children_up_1, children_down_1])
        new_population.append([children_up_2, children_down_2])

    new_population = [[mutate(pattern[0], mutation_chance, refresh_chance, schema, nonComparablePattern), 
        mutate(pattern[1], mutation_chance, refresh_chance, schema, nonComparablePattern)] for pattern in deepcopy(new_population)]
    new_population.append(bestPop)
    population = new_population
    return population, bestPop, mean, fitness_values[0]


def train_process(financial_data,schema, givenData, PipelineStepName, isBellow, nbRetry, preTrainedPattern, PatternSettings):
    population_size = 200
    mutation_chance = 0.015
    refresh_chance = 0.015
    oldBestFit = 0
    nbStuckFit = 0
    generation = 0
    lastNonOverfitGen = []
    lastNonOverFitValue = 0

    population = [generate_random_pattern(schema, PatternSettings) for _ in range(population_size)]
    population.append(givenData)
    bestPop = []
    financial_data.dropna(inplace=True)
    financial_data.reset_index(drop=True, inplace=True)
    while True:
        population , bestPop, meanFit, bestFit = getPreGen(financial_data, population_size, mutation_chance, refresh_chance, population, schema, PatternSettings, isBellow)
        generation += 1
        if (nbStuckFit == 1000):
            break
        if (oldBestFit == bestFit):
            nbStuckFit += 1
            population_size = min(max(200, nbStuckFit), 500)
            mutation_chance = min(max(0.015, nbStuckFit / 1000), 0.5)
            refresh_chance = min(max(0.015, (nbStuckFit * 0.5) / 1500), 0.2)
        else:
            population_size = 200
            mutation_chance = 0.025
            refresh_chance = 0.015
            nbStuckFit = 0
            oldBestFit = bestFit
            TESTFILEPATH = "./Pear2Pear/dataset_new_1h"
            dataset_filename = f"{TESTFILEPATH}.csv"
            testDataResult = pd.read_csv(dataset_filename)
            testDataResult = apply_patterns(testDataResult, preTrainedPattern)
            postTrainFit = evaluate_fitness(bestPop, testDataResult, isBellow)
            if (postTrainFit > lastNonOverFitValue):
                lastNonOverFitValue = postTrainFit
                lastNonOverfitGen = bestPop
        print(f"Epoch - {generation} Step_{PipelineStepName} nbRetry-{nbRetry}\n  BULL ->       {bestPop[0]}\n  BREAR ->      {bestPop[1]}\n  {bestFit} | {meanFit}\n  population_size={population_size} mutation_chance={mutation_chance * 100} refresh_chance={refresh_chance * 100} nbStuckFit={nbStuckFit} oldBestFit={oldBestFit}\n") 
    return bestPop, lastNonOverfitGen

def genetic_algorithm(training_set, initialPatterns, PatternSettings):
    FILEPATH = "./Pear2Pear/dataset_1h"
    dataset_filename = f"{FILEPATH}.csv"
    financial_data = pd.read_csv(dataset_filename)
    data = []
    patterns = []
    for idx, elem in enumerate(training_set):
        if (elem["status"]):
            continue

        isBellow = elem["isBellow"]
        schema = get_schema(elem["columns_list"])
        financial_data = apply_patterns(financial_data,patterns)    
        givenData = initialPatterns
        nbRetry = 0
        while(1):
            bestPop, givenData = train_process(financial_data, schema, givenData,elem["name"], isBellow, nbRetry, data, PatternSettings)
            TESTFILEPATH = os.getenv('TESTFILEPATH')
            dataset_filename = f"{TESTFILEPATH}.csv"
            testDataResult = pd.read_csv(dataset_filename)
            testDataResult = apply_patterns(testDataResult, data)
            postTrainFit = evaluate_fitness(bestPop, testDataResult, isBellow)
            preTrainedFit = evaluate_fitness(0, testDataResult, isBellow)

            if (postTrainFit > preTrainedFit):
                newData = {
                    "indicator": bestPop,
                    "isBellow": elem["isBellow"], 
                }
                data.append(newData)
                training_set[idx]["status"] = True
                print(f"Go to Next Step Training preTrainedFit={preTrainedFit} postTrainFit={postTrainFit}")
                break
            else : 
                print(f"Training prob overFit restart preTrainedFit={preTrainedFit} postTrainFit={postTrainFit}")
                nbRetry += 1
    print("Finished Pipeline")
