import os
import random
import numpy as np
import pandas as pd
from copy import deepcopy
from typing import Any, Dict, List, Sequence, Tuple, Optional, Union

import numba as nb
import multiprocess

from .GenUtils import apply_patterns, getSignal


def get_schema(collumns: Sequence[str]) -> List[Any]:
    """
    @brief Build a schema used to generate patterns.

    @param collumns Sequence[str] : list of column names used for pattern generation.
    @return List[Any] : schema used by pattern generator (list containing col names, ranges, comparators, etc.)
    """
    return [
        collumns,
        range(0, 4),
        [">", "<"],
        collumns,
        range(0, 4),
    ]


def generate_pattern(
    schema: Sequence[Any], PatternSettings: Dict[str, Any]
) -> List[Any]:
    """
    @brief Generate a single pattern using the provided schema and pattern settings.

    @param schema Sequence[Any] : schema produced by get_schema.
    @param PatternSettings Dict[str, Any] : mapping of pattern name -> settings describing comparativeRange and numberRange.

    Number range handling formula:
      result = random.uniform(min, max)

    @return List[Any] : generated pattern (list of elements matching schema positions).
    """
    pattern: List[Any] = [np.random.choice(rule) for rule in schema]
    firstPattern: Any = pattern[0]
    secondePattern: Any = pattern[3]

    firstPatternDescriptor: Dict[str, Any] = dict(PatternSettings[firstPattern])
    secondPatternDescriptor: Dict[str, Any] = dict(PatternSettings[secondePattern])

    # Ensure comparability by forcing patterns to be within each other's comparativeRange when needed
    if secondePattern not in firstPatternDescriptor["comparativeRange"]:
        secondePattern = deepcopy(firstPattern)
        secondPatternDescriptor = PatternSettings[secondePattern]

    if firstPattern not in secondPatternDescriptor["comparativeRange"]:
        firstPattern = deepcopy(secondePattern)
        firstPatternDescriptor = PatternSettings[firstPattern]

    # Possibly replace with a numeric range value
    if firstPatternDescriptor["numberRange"]["hasRange"] and np.random.rand() < 0.5:
        result = random.uniform(
            firstPatternDescriptor["numberRange"]["min"],
            firstPatternDescriptor["numberRange"]["max"],
        )
        # convert numeric to string as original code did
        secondePattern = str(result)

    # There were several problematic/duplicated conditions in original code.
    # Keep original intention — ensure positional indices differ when needed.
    try:
        # if same column index used for both comparative positions, shift the second index
        if pattern[1] == pattern[4]:
            pattern[1] = (pattern[1] + 1) if isinstance(pattern[1], int) else pattern[1]
    except Exception:
        # keep pattern unchanged if indexing issues
        pass

    pattern[0] = firstPattern
    pattern[3] = secondePattern
    return pattern


def generate_random_pattern(
    schema: Sequence[Any], PatternSettings: Dict[str, Any]
) -> List[List[List[Any]]]:
    """
    @brief Generate a randomized list of patterns (two lists of patterns, as in original code).

    @param schema Sequence[Any] : schema to use when generating patterns.
    @param PatternSettings Dict[str, Any] : pattern metadata/settings.

    @return List[List[List[Any]]] : patternList containing two lists; each list contains nbPattern patterns.
    """
    patternList: List[List[List[Any]]] = []
    nbPattern: int = random.randint(1, 4)

    for _ in range(2):
        fullPat: List[List[Any]] = [
            generate_pattern(schema, PatternSettings) for _ in range(nbPattern)
        ]
        patternList.append(fullPat)

    return patternList


@nb.njit()
def Process_Gain(
    start_rows: np.ndarray,
    formatted_candles: np.ndarray,
    multiplicator: int,
    processed_rows: np.ndarray,
    gain_index: int,
    flag_index: int,
    close_index: int,
    index_index: int,
    low_index: int,
    high_index: int,
) -> None:
    """
    @brief Compute the gain for entries starting at start_rows and store results in formatted_candles.

    @param start_rows np.ndarray : rows that are entry points (each row must contain an "index" field).
    @param formatted_candles np.ndarray : 2D array representation of the DataFrame to write gains into.
    @param multiplicator int : +1 for long positions, -1 for short positions.
    @param processed_rows np.ndarray : array of indices already processed (may be appended to).
    @param gain_index int : column index within formatted_candles corresponding to 'gain'.
    @param flag_index int : column index corresponding to trading flag ('Gflag').
    @param close_index int : column index for 'Close' price.
    @param index_index int : column index for the row index numeric embedding.
    @param low_index int : column index for 'Low' price.
    @param high_index int : column index for 'High' price.

    Formula:
      pct_variation = ((next_row_limit - start_close) / next_row_limit * 100) * multiplicator

    @return None
    """
    for start_row in start_rows:
        # start_row is expected to include an element representing the index at index_index
        if start_row[index_index] in processed_rows:
            continue
        upstart_index: int = int(start_row[index_index])
        current_index: int = upstart_index
        next_row_index: int = int(current_index + 1)
        while next_row_index < len(formatted_candles):
            next_row = formatted_candles[next_row_index]
            if next_row_index - current_index > 200:
                formatted_candles[upstart_index, gain_index] = -50
                break
            # choose limit depending on trade direction
            if multiplicator > 0:
                next_row_limit = next_row[low_index]
            else:
                next_row_limit = next_row[high_index]

            pct_variation = (
                (next_row_limit - start_row[close_index]) / next_row_limit * 100
            ) * multiplicator
            SLPct: int = -3
            if pct_variation <= SLPct:
                formatted_candles[upstart_index, gain_index] = SLPct
                break

            if multiplicator >= 0:
                if next_row[flag_index] == -1 or next_row[flag_index] == -2:
                    percentage_gain = (
                        (next_row[close_index] - start_row[close_index])
                        / start_row[close_index]
                    ) * 100
                    formatted_candles[upstart_index, gain_index] = (
                        percentage_gain * multiplicator
                    )
                    break
                else:
                    processed_rows = np.append(processed_rows, next_row_index)
            else:
                if next_row[flag_index] == 1 or next_row[flag_index] == -3:
                    percentage_gain = (
                        (next_row[close_index] - start_row[close_index])
                        / start_row[close_index]
                    ) * 100
                    formatted_candles[upstart_index, gain_index] = (
                        percentage_gain * multiplicator
                    )
                    break
                else:
                    processed_rows = np.append(processed_rows, next_row_index)
            next_row_index += 1


@nb.njit()
def Process_Wallet(
    npCopyData: np.ndarray, walletIndex: int, gains: np.ndarray, index_index: int
) -> None:
    """
    @brief Simulate wallet value progression using the gains array and write results into npCopyData.

    @param npCopyData np.ndarray : 2D array representing DataFrame content; wallet values will be updated in-place.
    @param walletIndex int : index in the array where wallet values are stored.
    @param gains np.ndarray : 1D array containing percentage gains (same length as rows).
    @param index_index int : column index for the row numeric index.

    Formula:
      gainValue = (gains[row_index] / 100) * prevValue
      value = prevValue + gainValue - fees_when_gain_exists

    @return None
    """
    for dataElem in npCopyData:
        index: int = int(dataElem[index_index])
        row_index = index
        if row_index < 1:
            prevValue = 1000.0
        else:
            prevValue = npCopyData[row_index - 1, walletIndex]
        gainValue = (gains[row_index] / 100) * prevValue
        value = gainValue + prevValue
        # if there is a gain, subtract a fee equal to 0.04% of prevValue (as in original)
        if gainValue:
            value = value - (prevValue * (0.04 / 100))
        npCopyData[row_index, walletIndex] = value


def evaluate_fitness(
    pattern: Union[List[Any], int, None], financial_data: pd.DataFrame, isBellow: bool
) -> float:
    """
    @brief Evaluate a pattern's fitness using profit factor.

    This function applies buy/sell signals to the financial_data, computes gains for each
    signal using Process_Gain, and returns the profit factor defined as:
      profit_factor = sum(profitable_trade_gains) / sum(abs(losing_trade_gains))

    @param pattern Union[List[Any], int, None] : pattern to evaluate; if falsy, evaluate without adding new pattern signals.
    @param financial_data pd.DataFrame : DataFrame with at least columns ['Gflag', 'Close', 'Low', 'High'].
    @param isBellow bool : controls an additional condition used when setting flags.

    @return float : profit_factor (may raise if dividing by zero; original code assumes there are losing trades).
    """
    copyData: pd.DataFrame
    if pattern:
        combined_condition_up: str = getSignal(pattern[0])  # type: ignore[index]
        combined_condition_down: str = getSignal(pattern[1])  # type: ignore[index]

        # evaluate the strings returned by getSignal in the local context (original code used eval)
        signals_up = eval(combined_condition_up)
        signals_down = eval(combined_condition_down)

        copyData = deepcopy(financial_data)
        copyData.loc[signals_down, "Gflag"] = -1
        copyData.loc[signals_up, "Gflag"] = 1
        if isBellow:
            cond = (financial_data["Gflag"] > 0) | (financial_data["Gflag"] < 0)
            copyData.loc[cond, "Gflag"] = financial_data.loc[cond, "Gflag"]
    else:
        copyData = deepcopy(financial_data)

    # initialize columns used by the numba functions
    copyData["gain"] = 0.0
    processed_rows: np.ndarray = np.array([-1])
    copyData.reset_index(drop=True, inplace=True)
    copyData["wallet"] = 1000.0
    copyData["index"] = copyData.index.values * 1.0

    upstart_rows = copyData[copyData["Gflag"] == 1]
    downstart_rows = copyData[copyData["Gflag"] == -1]

    # compute timeIn metric (original logic preserved)
    timeIn = 100 - (
        (len(financial_data) - (len(upstart_rows) + len(downstart_rows)))
        / len(financial_data)
        * 100
    )
    if timeIn < 2.5:
        return 0.0

    # determine column indices for the array view
    gain_index: int = copyData.columns.tolist().index("gain")
    flag_index: int = copyData.columns.tolist().index("Gflag")
    close_index: int = copyData.columns.tolist().index("Close")
    low_index: int = copyData.columns.tolist().index("Low")
    high_index: int = copyData.columns.tolist().index("High")
    index_index: int = copyData.columns.tolist().index("index")

    numpyData: np.ndarray = copyData.to_numpy()
    numpyUpStart: np.ndarray = upstart_rows.to_numpy()
    numpyDownStart: np.ndarray = downstart_rows.to_numpy()

    Process_Gain(
        numpyUpStart,
        numpyData,
        1,
        processed_rows,
        gain_index,
        flag_index,
        close_index,
        index_index,
        low_index,
        high_index,
    )

    Process_Gain(
        numpyDownStart,
        numpyData,
        -1,
        processed_rows,
        gain_index,
        flag_index,
        close_index,
        index_index,
        low_index,
        high_index,
    )

    copyData["gain"] = numpyData[:, gain_index]

    profitable_trades: float = np.sum(copyData[copyData["gain"] > 0]["gain"])
    losing_trades: float = np.sum(-copyData[copyData["gain"] < 0]["gain"])
    # avoid division by zero: if no losing trades, profit factor becomes large; mimic original behaviour
    if losing_trades == 0:
        # original code would crash; returning a very large number is an alternative,
        # but keep behaviour explicit: return inf to signal extreme performance
        return float("inf")

    profit_factor: float = float(profitable_trades / losing_trades)
    return profit_factor


def elitism(
    population: Sequence[List[Any]], fitness_values: Sequence[float], elitism_num: int
) -> List[List[Any]]:
    """
    @brief Select top `elitism_num` individuals from population based on fitness.

    @param population Sequence[List[Any]] : current population of patterns.
    @param fitness_values Sequence[float] : corresponding fitness values.
    @param elitism_num int : number of individuals to keep.

    @return List[List[Any]] : list of elite individuals (copied as lists).
    """
    elite_indices = np.argsort(fitness_values)[-elitism_num:]
    return [list(population[i]) for i in elite_indices]


def select_parents(
    population: list[list[list[Any]]], fitness_values: list[float]
) -> list[list[list[Any]]]:
    """
    @brief Select two parents from the population using fitness-proportionate selection.

    @param population Sequence[List[Any]] : population of candidate patterns.
    @param fitness_values Sequence[float] : fitness scores for each individual.

    Selection uses the roulette wheel method:
      pick a random number between 0 and sum(fitnesses) and choose the individual
      where the cumulative fitness crosses this value.

    @return List[List[Any]] : two selected parents (each copied to a list).
    """
    tempPopulation: List[List[Any]] = [list(x) for x in population]
    tempFiteness: List[float] = list(fitness_values)
    selected_parents: List[List[Any]] = []
    for _ in range(0, 2):
        total_fitness = np.sum(tempFiteness)
        # Protect against zero total fitness (choose random individual)
        if total_fitness == 0:
            rand_idx = random.randint(0, len(tempPopulation) - 1)
            selected_parents.append(list(tempPopulation[rand_idx]))
            continue

        selected_fitness = random.uniform(0, float(total_fitness))
        accumulated_fitness = 0.0
        for i, fitness in enumerate(tempFiteness):
            accumulated_fitness += fitness
            if accumulated_fitness >= selected_fitness:
                selected_parents.append(list(tempPopulation[i]))
                break
    return selected_parents


def reproduce(parent1: list[Any], parent2: list[Any]) -> tuple[list[Any], list[Any]]:
    """
    @brief Create two children by single-point crossover between parent1 and parent2.

    @param parent1 Sequence[Any] : first parent sequence.
    @param parent2 Sequence[Any] : second parent sequence.

    @return Tuple[List[Any], List[Any]] : child1 and child2 sequences.
    """
    # ensure split_point at least 1
    min_len = min(len(parent1), len(parent2))
    if min_len < 1:
        return list(parent1), list(parent2)
    split_point = max(np.random.randint(min_len), 1)
    child1 = list(parent1[:split_point]) + list(parent2[split_point:])
    child2 = list(parent2[:split_point]) + list(parent1[split_point:])
    return child1, child2


def mutate(
    pattern: List[Any],
    mutation_chance: float,
    refresh_chance: float,
    schema: Sequence[Any],
    nonComparablePattern: Dict[str, Any],
) -> List[Any]:
    """
    @brief Mutate a pattern with a given mutation chance, or refresh it entirely.

    @param pattern List[Any] : pattern to mutate in-place (but a new pattern is returned).
    @param mutation_chance float : probability of applying a mutation.
    @param refresh_chance float : probability of refreshing the entire pattern.
    @param schema Sequence[Any] : schema for pattern generation.
    @param nonComparablePattern Dict[str, Any] : pattern settings to pass to generator.

    @return List[Any] : mutated or refreshed pattern.
    """
    if len(pattern) == 0:
        return pattern
    paternMut: int = np.random.randint(len(pattern))
    if np.random.rand() < refresh_chance:
        return generate_random_pattern(schema, nonComparablePattern)[0]
    elif np.random.rand() < mutation_chance:
        pattern_copy = pattern.copy()
        pattern_copy[paternMut] = generate_random_pattern(schema, nonComparablePattern)[
            0
        ][0]
        return pattern_copy

    return pattern


def evaluate_fitness_wrapper(args: Tuple[Any, pd.DataFrame, bool]) -> float:
    """
    @brief Wrapper used for multiprocessing pool mapping.

    @param args Tuple[pattern, financial_data, isBellow]
    @return float : fitness value computed by evaluate_fitness
    """
    pattern, financial_data, isBellow = args
    fitness = evaluate_fitness(pattern, financial_data, isBellow)
    return fitness


def getPreGen(
    financial_data: pd.DataFrame,
    population_size: int,
    mutation_chance: float,
    refresh_chance: float,
    population: List[List[Any]],
    schema: Sequence[Any],
    nonComparablePattern: Dict[str, Any],
    isBellow: bool,
) -> Tuple[List[List[Any]], List[Any], float, float]:
    """
    @brief Evaluate current population with multiprocessing, create next generation using selection/reproduction/mutation.

    @param financial_data pd.DataFrame : data used for fitness evaluation.
    @param population_size int : desired size of next generation.
    @param mutation_chance float : mutation probability.
    @param refresh_chance float : refresh probability.
    @param population List[List[Any]] : current population (list of [up_pattern, down_pattern] pairs).
    @param schema Sequence[Any] : schema for regeneration.
    @param nonComparablePattern Dict[str, Any] : PatternSettings to be used for generation.
    @param isBellow bool : flag forwarded to evaluate_fitness.

    @return Tuple[List[List[Any]], List[Any], float, float] :
        - new population,
        - bestPop (best individual),
        - mean fitness across old population,
        - best fitness value (first element of sorted fitness list).
    """
    eval_args: List[Tuple[Any, pd.DataFrame, bool]] = [
        (pattern, financial_data, isBellow) for pattern in population
    ]

    # limit processes to min(10, population size)
    processes = min(10, len(population))
    with multiprocess.Pool(processes=processes) as pool:
        fitness_values: List[float] = pool.map(evaluate_fitness_wrapper, eval_args)

    mean = float(np.mean(fitness_values))
    # sort by fitness descending
    sorted_indices = np.argsort(fitness_values)[::-1]
    population = [population[i] for i in sorted_indices]
    fitness_values = [fitness_values[i] for i in sorted_indices]

    bestPop = deepcopy(population[0])
    new_population: List[List[Any]] = []

    # produce children until we have enough
    while len(new_population) < population_size:
        parents = select_parents(population, fitness_values)
        # parents are expected to be in shape [ [up_pattern, down_pattern], ... ]
        children_up_1, children_up_2 = reproduce(parents[0][0], parents[1][0])
        children_down_1, children_down_2 = reproduce(parents[0][1], parents[1][1])
        new_population.append([children_up_1, children_down_1])
        new_population.append([children_up_2, children_down_2])

    # mutate/populate new_generation
    new_population = [
        [
            mutate(
                pattern[0],
                mutation_chance,
                refresh_chance,
                schema,
                nonComparablePattern,
            ),
            mutate(
                pattern[1],
                mutation_chance,
                refresh_chance,
                schema,
                nonComparablePattern,
            ),
        ]
        for pattern in deepcopy(new_population)
    ]

    # keep best from previous generation (elitism)
    new_population.append(bestPop)
    population = new_population
    best_fitness_value = float(fitness_values[0]) if fitness_values else 0.0
    return population, bestPop, mean, best_fitness_value


def train_process(
    financial_data: pd.DataFrame,
    schema: Sequence[Any],
    givenData: List[Any],
    PipelineStepName: str,
    isBellow: bool,
    nbRetry: int,
    preTrainedPattern: List[Any],
    PatternSettings: Dict[str, Any],
) -> Tuple[List[Any], List[Any]]:
    """
    @brief Train a generational genetic algorithm loop until convergence or a stop condition.

    @param financial_data pd.DataFrame : training data.
    @param schema Sequence[Any] : schema for pattern generation.
    @param givenData List[Any] : initial pattern(s) given to the training (seed).
    @param PipelineStepName str : textual name for debugging/printing.
    @param isBellow bool : flag forwarded to evaluate_fitness.
    @param nbRetry int : number of retries already performed externally.
    @param preTrainedPattern List[Any] : patterns applied when testing overfitting.
    @param PatternSettings Dict[str, Any] : pattern metadata/settings.

    The function runs an indefinite loop until nbStuckFit >= 1000 or a break condition triggers.
    It returns the best population and the last known non-overfit best patterns.

    @return Tuple[List[Any], List[Any]] : (bestPop, lastNonOverfitGen)
    """
    population_size: int = 200
    mutation_chance: float = 0.015
    refresh_chance: float = 0.015
    oldBestFit: float = 0.0
    nbStuckFit: int = 0
    generation: int = 0
    lastNonOverfitGen: List[Any] = []
    lastNonOverFitValue: float = 0.0

    population: List[List[Any]] = [
        generate_random_pattern(schema, PatternSettings) for _ in range(population_size)
    ]
    population.append(givenData)
    bestPop: List[Any] = []
    financial_data = financial_data.dropna().reset_index(drop=True)

    while True:
        population, bestPop, meanFit, bestFit = getPreGen(
            financial_data,
            population_size,
            mutation_chance,
            refresh_chance,
            population,
            schema,
            PatternSettings,
            isBellow,
        )
        generation += 1
        if nbStuckFit == 1000:
            break

        if oldBestFit == bestFit:
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

            # Load test dataset for overfitting check (keeps original behaviour)
            TESTFILEPATH = "./Pear2Pear/dataset_new_1h"
            dataset_filename = f"{TESTFILEPATH}.csv"
            testDataResult = pd.read_csv(dataset_filename)
            testDataResult = apply_patterns(testDataResult, preTrainedPattern)
            postTrainFit = evaluate_fitness(bestPop, testDataResult, isBellow)
            if postTrainFit > lastNonOverFitValue:
                lastNonOverFitValue = postTrainFit
                lastNonOverfitGen = deepcopy(bestPop)

        print(
            f"Epoch - {generation} Step_{PipelineStepName} nbRetry-{nbRetry}\n"
            f"  BULL ->       {bestPop[0] if isinstance(bestPop, (list, tuple)) and len(bestPop) > 0 else bestPop}\n"
            f"  BREAR ->      {bestPop[1] if isinstance(bestPop, (list, tuple)) and len(bestPop) > 1 else ''}\n"
            f"  {bestFit} | {meanFit}\n"
            f"  population_size={population_size} mutation_chance={mutation_chance * 100} "
            f"refresh_chance={refresh_chance * 100} nbStuckFit={nbStuckFit} oldBestFit={oldBestFit}\n"
        )

    return bestPop, lastNonOverfitGen


def genetic_algorithm(
    training_set: Sequence[Dict[str, Any]],
    initialPatterns: List[Any],
    PatternSettings: Dict[str, Any],
) -> None:
    """
    @brief Run the pipeline over the training_set, training patterns sequentially.

    @param training_set Sequence[Dict[str, Any]] : list of steps; each element should include keys:
            - "status": bool, skip step if True
            - "isBellow": bool
            - "columns_list": list of column names
            - "name": string
    @param initialPatterns List[Any] : initial patterns to seed training
    @param PatternSettings Dict[str, Any] : pattern metadata/settings used by generators

    This function reads a dataset (path hardcoded in original function), iterates the training_set,
    and appends discovered patterns to `data` when post-training fitness is better than pre-trained baseline.

    @return None
    """
    FILEPATH = "./Pear2Pear/dataset_1h"
    dataset_filename = f"{FILEPATH}.csv"
    financial_data = pd.read_csv(dataset_filename)

    data: List[Dict[str, Any]] = []
    patterns: List[Any] = []

    for idx, elem in enumerate(training_set):
        if elem.get("status"):
            continue

        isBellow: bool = bool(elem.get("isBellow", False))
        schema = get_schema(elem["columns_list"])
        # apply existing patterns to financial_data
        financial_data = apply_patterns(financial_data, patterns)
        givenData = initialPatterns
        nbRetry: int = 0
        while True:
            bestPop, givenData = train_process(
                financial_data,
                schema,
                givenData,
                elem["name"],
                isBellow,
                nbRetry,
                data,
                PatternSettings,
            )
            TESTFILEPATH = os.getenv("TESTFILEPATH")
            if not TESTFILEPATH:
                # fallback to the same path used in train_process to preserve behaviour
                TESTFILEPATH = "./Pear2Pear/dataset_new_1h"
            dataset_filename = f"{TESTFILEPATH}.csv"
            testDataResult = pd.read_csv(dataset_filename)
            testDataResult = apply_patterns(testDataResult, data)
            postTrainFit = evaluate_fitness(bestPop, testDataResult, isBellow)
            preTrainedFit = evaluate_fitness(0, testDataResult, isBellow)

            if postTrainFit > preTrainedFit:
                newData = {
                    "indicator": bestPop,
                    "isBellow": elem["isBellow"],
                }
                data.append(newData)
                # mark step as completed
                if isinstance(training_set, list) and idx < len(training_set):
                    training_set[idx]["status"] = True
                print(
                    f"Go to Next Step Training preTrainedFit={preTrainedFit} postTrainFit={postTrainFit}"
                )
                break
            else:
                print(
                    f"Training prob overFit restart preTrainedFit={preTrainedFit} postTrainFit={postTrainFit}"
                )
                nbRetry += 1

    print("Finished Pipeline")
