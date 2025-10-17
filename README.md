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

### Usando prompt de comando **(recomendado)**: 

Basta estar no diretório principal 'compilador_em_python/' e digitar o comando no terminal:

```
python main.py
```

Exemplo:

![executando_ide](./images_documentation/exercutando_codigo_prompt_comando.png)

### Usando uma IDE:

Basta selecionar o arquivo `main.py` e clicar no botão 'run' da IDE.

Exemplo com o VS Code (clicar onde estão as setas vermelhas):

![executando_ide](./images_documentation/exercutando_codigo_ide_vs_code.png)

### Entrada do sistema 

Seja em prompt ou em IDE, aparecerá um catálogo com todos exemplos da pasta `tonto_examples` enumerados.

![exemplos_enumerados](./images_documentation/exemplos_enumerados.png)

Para executar o compilador no exemplo escolhido basta digitar o respectivo número, por exemplo, se quiser executar o `car.tonto`, digite 01 e tecle 'enter' no seu teclado.

### Saída do sistema 

- Confirmação do arquivo escolhido;
- Breve log de executando e concluído;
- Tabela de tokens:

    - Id do Token,
    - Valor encontrado,
    - Tipo do valor (classe, relação, instância ou o próprio valor (caso seja palavra-chave ou terminal))
    - Linha que o token está,
    - Coluna que o token inicia,
    - Classificação conforme o que foi dado no arquivo (classes, relações, palavras-chave, indivíduos (instâncias, se houver), 
palavras reservadas e meta-atributos)

- Tabela de contagem das classificações.

![exemplos_tabela_tokens](./images_documentation/saida_tabela_tokens.png)

![exemplos_contagem_classificacao](./images_documentation/tabela_contagem_classificacao.png)
