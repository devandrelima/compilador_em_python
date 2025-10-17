# **Estrutura do Projeto**

### Organização das pastas

```
COMPILADOR_EM_PYTHON/
│
├── .gitignore
├── main.py
├── README.md
│
├── lexico_analyzer/
│   ├── __init__.py
│   ├── analyzer.py
│   └── __pycache__/ (arquivos de cache, por favor, desconsiderar)
│
└── tonto_examples/
    ├── alergiaalimentar.tonto
    ├── car.tonto
    ├── ...todos os exemplos utilizados no código

```

-----

### **Descrição dos Componentes**

  * `main.py`

      * É o ponto de entrada principal do projeto. Ele atua como o "orquestrador" do compilador, responsável por chamar as diferentes fases da compilação (atualmente, apenas a análise léxica) e gerenciar o fluxo geral do programa.

  * `README.md`

      * Arquivo de documentação principal do projeto. Descreve o que o projeto faz, como instalá-lo, como usá-lo e quaisquer outras informações importantes para quem for utilizá-lo.

  * `.gitignore`

      * É um arquivo de configuração do Git. Ele especifica quais arquivos e pastas devem ser ignorados pelo sistema de controle de versão (Git). É fundamental para manter o repositório limpo, excluindo arquivos temporários e gerados automaticamente, como a pasta `__pycache__`.

  * `lexico_analyzer/` (Diretório)

      * Este é um pacote Python que encapsula toda a lógica do **Analisador Léxico**.
      * `__init__.py`: Este arquivo, mesmo que vazio, sinaliza ao Python que o diretório 'lexico_analyzer' pode ser importado como um módulo. É o que permite que o 'main.py' execute 'from lexico_analyzer.analyzer import main_analyser'.
      * `analyzer.py`: Contém todo o código-fonte do analisador léxico, construído com a biblioteca PLY. Ele define os tokens, as regras de reconhecimento e a função principal que processa um arquivo '.tonto'.
      * `__pycache__/`: Uma pasta gerada automaticamente pelo Python. Ela armazena versões compiladas (bytecode) do código '.pyc' para acelerar a inicialização do programa. Esta pasta pode ser ignorada e excluída com segurança.

  * `tonto_examples/` (Diretório)

      * Este diretório armazena todos os arquivos de código-fonte na linguagem **Tonto** que servem como exemplos e casos de teste para o compilador.
      * `alergiaalimentar.tonto`, `car.tonto`, `carRentail.tonto`, entre outros arquivos '.tonto': Cada um desses arquivos pode ser lido pelo `main.py` para testar o funcionamento do analisador léxico.

# **Instalações necessárias para executar o projeto**:

### Comandos executados para instalação do python do zero:

```
sudo apt update

sudo apt install python3

sudo apt install python3-pip
```


### instalação do PLY para analisador léxico

```
pip install ply
```

### instalação do tabulate para mostrar tabela

```
pip install tabulate
```


# **Como executar o projeto**:

Após as instalações necessárias, para executar o projeto de forma concisa basta rodar o arquivo `main.py`.

- Usando uma IDE: Basta selecionar o arquivo `main.py` e clicar no botão 'run'

- Usando prompt de comando (recomendado): Basta estar no diretório principal 'compilador_em_python/' e digitar o comando no terminal:

```
python main.py
```