import os 

def writer(nome, mmsi):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_dir, '../data/list_boats.txt')

    # Verifica se o arquivo já existe e se já contém conteúdo
    with open(file_path, 'r') as file:
        lines = file.readlines()

    # Abre o arquivo para append
    with open(file_path, 'a') as file:
        # Se houver linhas no arquivo e a última não tiver uma nova linha, adiciona uma nova linha
        if lines and not lines[-1].endswith('\n'):
            file.write('\n')
        # Escreve o novo conteúdo sem linha extra no início
        file.write(f'NAME: {nome}, MMSI: {mmsi}\n')

def delete(nome=None, mmsi=None):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_dir, '../data/list_boats.txt')

    # Lê todas as linhas do arquivo
    with open(file_path, 'r') as file:
        lines = file.readlines()

    # Abre o arquivo para escrita, substituindo o conteúdo existente
    with open(file_path, 'w') as file:
        for line in lines:
            # Verifica se a linha contém o nome ou o mmsi que deve ser excluído
            if (nome and nome in line) or (mmsi and mmsi in line):
                continue
            if line.strip(): # Se não contiver, escreve a linha no arquivo
                file.write(line.strip() + '\n')

#função de leitura de arquivo
def read_file(file_path):
    list_MMSI = []
    list_boats = []
    with open(file_path, 'r') as file:
        for line in file.readlines():
            parts = line.split(',') #divide a linha em strings de acordo com a vírgula
            if len(parts) >= 2: #verifica se a linha tem pelo menos 2 elementos
                list_boats.append(parts[0].strip().replace('NAME: ', '')) #parts[0] pega o primeiro elemento da lista parts, no caso o nome do barco
                list_MMSI.append(parts[-1].strip().replace('MMSI: ', '')) #parts[-1] pega o último elemento da lista parts, no caso o MMSI:+numero 
                #strip() remove espaços em branco e replace() retira mmsei e deixa só o número

    return list_boats, list_MMSI

