import docker

def get_logs(container_name):
    """
    Verilen container adından son 200 satırlık logları alır.
    """
    try:
        client = docker.from_env()
        container = client.containers.get(container_name)
        logs = container.logs(tail=200).decode("utf-8", errors="ignore")
        return logs
    except Exception as e:
        print(f"Error while getting logs: {e}")
        return None
