import random
import math
import numpy as np  # Thêm thư viện numpy để tính toán hiệu quả
import time  # Thêm thư viện time để tính thời gian chạy
import logging  # Thêm thư viện logging để ghi log
from typing import List, Tuple, Dict, Any  # Thêm type hints

# Cấu hình logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def knapsack_simulated_annealing(
    item_names: List[str],
    item_values: List[int],
    item_weights: List[int],
    knapsack_capacity: int,
    initial_temperature: float = 10000,
    cooling_rate: float = 0.95,
    max_iterations: int = 1000
) -> Tuple[List[str], List[str], float]:
    """
    Giải bài toán knapsack bằng thuật toán Simulated Annealing.
    
    Args:
        item_names: Danh sách tên các vật phẩm
        item_values: Danh sách giá trị của các vật phẩm
        item_weights: Danh sách trọng lượng của các vật phẩm
        knapsack_capacity: Trọng lượng tối đa của balo
        initial_temperature: Nhiệt độ ban đầu của thuật toán
        cooling_rate: Tỷ lệ làm mát nhiệt độ sau mỗi vòng lặp
        max_iterations: Số vòng lặp tối đa
        
    Returns:
        Tuple chứa (danh sách vật phẩm được chọn, lịch sử giải pháp, thời gian chạy)
    """
    # Không sử dụng hạt giống cố định để duy trì tính ngẫu nhiên đích thực
    
    # Bắt đầu đo thời gian
    start_time = time.time()
    
    # Khởi tạo giải pháp ban đầu: ba lô rỗng
    current_solution = np.zeros(len(item_names), dtype=int)  # Sử dụng numpy array
    current_value = 0
    current_weight = 0

    # Lịch sử các giải pháp để trực quan hóa
    solution_history = []

    # Hàm tính tổng giá trị và tổng trọng lượng của một giải pháp
    def calculate_solution_value_weight(solution: np.ndarray) -> Tuple[int, int]:
        """Tính tổng giá trị và trọng lượng của giải pháp."""
        selected_indices = np.where(solution == 1)[0]
        total_value = np.sum(np.array(item_values)[selected_indices])
        total_weight = np.sum(np.array(item_weights)[selected_indices])
        return total_value, total_weight

    # Hàm sinh ra một giải pháp láng giềng bằng cách đảo ngược một vật phẩm ngẫu nhiên
    def generate_neighbor_solution(solution: np.ndarray) -> np.ndarray:
        """Sinh giải pháp láng giềng bằng cách đảo ngược một vật phẩm ngẫu nhiên."""
        new_solution = solution.copy()
        index = random.randint(0, len(solution) - 1)
        new_solution[index] = 1 - new_solution[index]
        return new_solution

    # Khởi tạo nhiệt độ ban đầu
    current_temperature = initial_temperature
    best_solution = current_solution.copy()
    best_value, best_weight = calculate_solution_value_weight(best_solution)

    # Các biến thống kê
    accepted_solutions = 0
    rejected_solutions = 0
    
    # Thêm mức nhiệt độ tối thiểu để tránh Math Range Error
    MIN_TEMPERATURE = 0.00001
    
    logger.info(f"Bắt đầu thuật toán Simulated Annealing với {len(item_names)} vật phẩm")
    logger.info(f"Trọng lượng tối đa: {knapsack_capacity}")

    for iteration in range(max_iterations):
        # Sinh ra một giải pháp láng giềng
        new_solution = generate_neighbor_solution(current_solution)
        new_value, new_weight = calculate_solution_value_weight(new_solution)

        # Kiểm tra nếu giải pháp mới tốt hơn hoặc chấp nhận giải pháp tồi hơn theo xác suất
        is_acceptable = new_weight <= knapsack_capacity
        is_better = new_value > current_value
        
        # Kiểm tra nhiệt độ và xử lý để tránh Math Range Error
        # Tránh chia cho số quá nhỏ và giới hạn giá trị quá lớn trong mũ
        if current_temperature < MIN_TEMPERATURE:
            current_temperature = MIN_TEMPERATURE
            
        # Tính xác suất chấp nhận giải pháp tồi hơn một cách an toàn
        # Tránh overflow khi exp() nhận giá trị quá lớn
        if new_value < current_value:
            # Giới hạn số âm trong hàm mũ để tránh underflow
            exponent = max(-700, (new_value - current_value) / current_temperature)
            probability = math.exp(exponent)
        else:
            probability = 1.0  # Luôn chấp nhận giải pháp tốt hơn
            
        accept_worse = random.random() < probability
        
        if is_acceptable and (is_better or accept_worse):
            current_solution = new_solution.copy()
            current_value = new_value
            current_weight = new_weight
            accepted_solutions += 1

            # Cập nhật giải pháp tốt nhất nếu giải pháp hiện tại tốt hơn
            if current_value > best_value:
                best_solution = current_solution.copy()
                best_value = current_value
                best_weight = new_weight
        else:
            rejected_solutions += 1

        # Thêm thông tin về lần lặp hiện tại vào lịch sử
        iter_info = {
            'iteration': iteration,
            'value': current_value,
            'weight': current_weight,
            'temperature': current_temperature,
            'accepted': is_acceptable and (is_better or accept_worse)
        }
        
        # Lưu lịch sử dưới dạng chuỗi để hiển thị trong giao diện
        history_entry = f"Lần {iteration}: Giá trị: {current_value}, Trọng lượng: {current_weight}, Nhiệt độ: {current_temperature:.6f}"
        solution_history.append(history_entry)

        # Giảm nhiệt độ theo tỷ lệ làm mát
        current_temperature *= cooling_rate
        
        # Log mỗi 100 lần lặp
        if iteration % 100 == 0:
            logger.info(f"Lần lặp {iteration}: Giá trị tốt nhất = {best_value}, Trọng lượng = {best_weight}")

    # Kết thúc đo thời gian
    execution_time = time.time() - start_time
    
    # Xác định các vật phẩm được chọn trong giải pháp tốt nhất
    selected_items = [item_names[i] for i, taken in enumerate(best_solution) if taken == 1]
    
    # Thống kê kết quả
    logger.info(f"Hoàn thành sau {execution_time:.4f} giây")
    logger.info(f"Giải pháp tốt nhất: Giá trị = {best_value}, Trọng lượng = {best_weight}")
    logger.info(f"Số giải pháp được chấp nhận: {accepted_solutions}")
    logger.info(f"Số giải pháp bị từ chối: {rejected_solutions}")

    return selected_items, solution_history, execution_time

# Hàm để tạo dữ liệu ngẫu nhiên cho bài toán knapsack
def generate_knapsack_data(num_items: int, max_value: int = 500, max_weight: int = 20) -> Dict[str, List]:
    """
    Tạo dữ liệu ngẫu nhiên cho bài toán knapsack.
    
    Args:
        num_items: Số lượng vật phẩm cần tạo
        max_value: Giá trị tối đa của một vật phẩm
        max_weight: Trọng lượng tối đa của một vật phẩm
        
    Returns:
        Dictionary chứa danh sách tên, giá trị và trọng lượng
    """
    item_names = [f"Product_{i+1}" for i in range(num_items)]
    item_values = [random.randint(1, max_value) for _ in range(num_items)]
    item_weights = [random.randint(1, max_weight) for _ in range(num_items)]
    
    return {
        'names': item_names,
        'values': item_values,
        'weights': item_weights
    }