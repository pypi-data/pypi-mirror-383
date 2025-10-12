from multimodalsim_viewer.server.data_manager import SimulationVisualizationDataManager


def register_log(simulation_id, message):
    saved_logs_directory_path = SimulationVisualizationDataManager.get_saved_logs_directory_path()
    file_name = f"{simulation_id}.txt"
    file_path = f"{saved_logs_directory_path}/{file_name}"

    with open(file_path, "a", encoding="utf-8") as file:
        file.write(message + "\n")
