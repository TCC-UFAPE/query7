import requests
import pandas as pd
import time

BASE_URL = "https://vulnerabilityhistory.org/api"

def get_project_data():
    print("Buscando a lista de todos os projetos...")
    try:
        response = requests.get(f"{BASE_URL}/projects", timeout=30)
        response.raise_for_status()
        all_projects = response.json()
        print(f"Encontrados {len(all_projects)} projetos.")
        
        project_map = {
            p['subdomain']: {
                'id': p['id'],
                'name': p['name']
            }
            for p in all_projects if 'subdomain' in p
        }
        return project_map
        
    except requests.exceptions.RequestException as e:
        print(f"\n--- ERRO AO BUSCAR LISTA DE PROJETOS: {e} ---")
        return None

def fetch_vulnerabilities_for_project(project_id):
    """Busca todas as vulnerabilidades para um ID de projeto específico."""
    params = {'project_id': project_id, 'limit': 10000}
    try:
        print(f"    Buscando vulnerabilidades para o projeto ID: {project_id}...")
        response = requests.get(f"{BASE_URL}/vulnerabilities", params=params)
        response.raise_for_status()
        
        vulnerabilities = response.json() 
        
        print(f"    Encontradas {len(vulnerabilities)} vulnerabilidades.")
        return vulnerabilities
    except requests.exceptions.RequestException as e:
        print(f"    Erro ao buscar vulnerabilidades para o projeto {project_id}: {e}")
        return []

def run_task_1_and_2(project_data):
    print("\n--- Iniciando Tarefa 1 & 2: Contagem de Vulnerabilidades ---")
    if not project_data:
        print("Dados de projeto não disponíveis. Pulando tarefa.")
        return

    data = []
    for subdomain, details in project_data.items():
        project_name = details['name']
        project_id = details['id']
        print(f"Processando contagens para o projeto: {project_name}")
        
        vulnerabilities = fetch_vulnerabilities_for_project(project_id)
        
        total_count = len(vulnerabilities)
        curated_count = sum(1 for v in vulnerabilities if v.get('curated', False))
        
        data.append({
            'Projeto': project_name,
            'Vulnerabilidades Totais Documentadas': total_count,
            'Vulnerabilidades Curadas': curated_count
        })
        time.sleep(1)
            
    df = pd.DataFrame(data)
    filename = "1_2_vulnerabilidades_por_projeto.xlsx"
    df.to_excel(filename, index=False)
    print(f"-> Sucesso! Arquivo '{filename}' gerado.")

def run_task_3_by_type(project_data):
    print("\n--- Iniciando Tarefa 3: Vulnerabilidades por Tipo ---")
    if not project_data:
        return

    all_type_counts = {}
    for subdomain, details in project_data.items():
        project_name = details['name']
        print(f"Processando tipos para o projeto: {project_name}")
        
        vulnerabilities = fetch_vulnerabilities_for_project(details['id'])
        type_counts = {}
        for vuln in vulnerabilities:
            vuln_type = vuln.get('vulnerability_type', 'N/A')
            type_counts[vuln_type] = type_counts.get(vuln_type, 0) + 1
        
        all_type_counts[project_name] = type_counts
        time.sleep(1)

    df = pd.DataFrame.from_dict(all_type_counts, orient='index').fillna(0).astype(int)
    df = df.rename_axis('Projeto').reset_index()
    
    filename = "3_vulnerabilidades_por_tipo.xlsx"
    df.to_excel(filename, index=False)
    print(f"-> Sucesso! Arquivo '{filename}' gerado.")

def run_task_4_by_lesson(project_data):
    print("\n--- Iniciando Tarefa 4: Vulnerabilidades por Lição (Lesson) ---")
    if not project_data:
        return

    all_lesson_counts = {}
    for subdomain, details in project_data.items():
        project_name = details['name']
        print(f"Processando lições para o projeto: {project_name}")

        vulnerabilities = fetch_vulnerabilities_for_project(details['id'])
        lesson_counts = {}
        for vuln in vulnerabilities:
            if vuln.get('curated'):
                lesson = vuln.get('vhp_lesson', 'N/A')
                lesson_counts[lesson] = lesson_counts.get(lesson, 0) + 1
        
        all_lesson_counts[project_name] = lesson_counts
        time.sleep(1) 

    df = pd.DataFrame.from_dict(all_lesson_counts, orient='index').fillna(0).astype(int)
    df = df.rename_axis('Projeto').reset_index()

    filename = "4_vulnerabilidades_por_licao.xlsx"
    df.to_excel(filename, index=False)
    print(f"-> Sucesso! Arquivo '{filename}' gerado.")

def run_task_5_words_written(project_data):
    print("\n--- Iniciando Tarefa 5: Contagem de Palavras por Documentação ---")
    if not project_data:
        return
        
    all_vuln_words = []
    for subdomain, details in project_data.items():
        project_name = details['name']
        print(f"Processando contagem de palavras para o projeto: {project_name}")
        
        vulnerabilities = fetch_vulnerabilities_for_project(details['id'])
        for vuln in vulnerabilities:
            if vuln.get('curated'):
                notes = vuln.get('notes', '')
                word_count = len(notes.split()) if notes else 0
                all_vuln_words.append({
                    'Projeto': project_name,
                    'CVE': vuln.get('cve', 'N/A'),
                    'Contagem de Palavras (Curadoria)': word_count
                })
        time.sleep(1) 
        
    df = pd.DataFrame(all_vuln_words)
    filename = "5_contagem_palavras_curadoria.xlsx"
    df.to_excel(filename, index=False)
    print(f"-> Sucesso! Arquivo '{filename}' gerado.")


if __name__ == "__main__":
    print("Coletando dados do The Vulnerability History Project...")
    project_info = get_project_data()
    
    if project_info:
        run_task_1_and_2(project_info)
        run_task_3_by_type(project_info)
        run_task_4_by_lesson(project_info)
        run_task_5_words_written(project_info)
        
        print("\nTodas as tarefas foram concluídas com sucesso!")
    else:
        print("\nNão foi possível obter os dados iniciais dos projetos. O script não pode continuar.")