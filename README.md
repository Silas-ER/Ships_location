<!--<p align="center"><a href="#"><img src="src/icon.jpeg" width="350"></a></p>-->

# Sistema de Consulta de Localização de Veículos Marítimos

Repositório dedicado ao estudo do funcionamento do streamlit para desenvolvimento web integrado com APIs.

## Sobre o projeto

<p>
  O intuito do projeto é a partir de uma lista de barcos fornecida pelo usuário identificar inicialmente a posição atual (ou mais recente) em um mapa, posteriormente explorar as funcionalidades
  da API, obtendo dados históricos de movimentações dos veículos e por fim averiguar a possibilidade de consulta individual ou filtrada de dados sobre barcos. 
</p>

## Tecnologia Utilizada
<p align="center"><a href="https://docs.streamlit.io/" target="_blank"><img src="https://streamlit.io/images/brand/streamlit-logo-secondary-colormark-lighttext.png" width="400"></a></p>

## About Streamlit
O Streamlit é uma biblioteca Python de código aberto que permite criar aplicativos web de forma rápida e intuitiva, especialmente para visualização de dados e aplicações de machine learning.
<br>

Streamlit facilita a implementação de tarefas comuns em projetos web, como:

- [Desenvolvimento de chats;](https://docs.streamlit.io/develop/tutorials/llms).
- [Multipáginas;](https://docs.streamlit.io/develop/tutorials/multipage).
- [Conexões à diferentes fontes de dados;](https://docs.streamlit.io/develop/tutorials/databases).
- [Execução de scripts.](https://docs.streamlit.io/develop/tutorials/execution-flow).

Streamlit é acessível, oferecendo ferramentas necessárias para a construção de pequenas aplicações web.

## Learning Streamlit

O [Streamlit](https://docs.streamlit.io/) possui uma documentação crescente com cada vez mais funcionalidades sendo criadas, facilitando o aprendizado para desenvolvedores de nível básico. Além da documentação oficial, há uma grande variedade de tutoriais e guias disponíveis para ajudar a dominar o framework.

## Construção do App

A [API](https://static.loongship.com/dataApi/api.html#_3-1-%E8%88%B9%E8%88%B6%E6%90%9C%E7%B4%A2) utilizada para a construção do projeto foi a do site [SHIPDT](https://www.shipdt.com/), a qual os usuários tinham mais familiaridade com a disposição dos dados que vinham nos resultados. Ela tem diversas opções de retorno de dados como temperatura da água, condições climáticas, entre outras, mas procurei focar na parte solicitada. 
<br>
O app foi construido com base em um menu lateral feito com o componente ```st.navigation``` contendo todas as solicitações feitas anteriormente na descrição do projeto, separadas por blocos utilizando o ```st.Page```. Ao abrir o "site" hospedado localmente o usuário se depara com a página inicial: <br>

<div align="center">
  <a href="#"><img src="src/1.png" width="900"></a>
  <p>Que mostra os dados de última localizção (mais recente) de cada barco que esteja incluido numa lista contendo NOME e MMSI que são utilizados como parâmetro para pesquisa na API.</p>
</div>

<br>

<div align="center">
  <a href="#"><img src="src/2.png" width="900"></a>
  <p>Continuando a página o usuário encontrará os dados referentes a pesquisa retornada, em formato de "tabela", esse dados geralmente retornam da API em formato .json</p>
</div>

<br>

<div align="center">
  <a href="#"><img src="src/3.png" width="900"></a>
  <p>Para alternar entre as páginas, utilizamos um menu lateral, como pode ser visto na imagem.</p>
</div>

<br>

<div align="center">
  <a href="#"><img src="src/4.png" width="900"></a>
  <p>Na página de histórico de movimentação temos dois data inputs para uma data inicial e final utilizados como intervalo para pesquisa, e um select box gerado a partir a lista informada anteriormente.
  Com isso é gerado um mapa com todas as movimentações do barco naquele período, unidas por linhas setadas.</p>
</div>

<br>

<div align="center">
  <a href="#"><img src="src/5.png" width="900"></a>
  <p>Afim de manter a coerência da leitura do código, inplementei a possibilidade do usuário inserir novos barcos ou excluir do sistema através de uma página especifica, evitando inserções de maneira
  diferente e mantendo a constância do script.</p>
</div>

<br>

<div align="center">
  <a href="#"><img src="src/6.png" width="900"></a>
  <p>Por fim, temos a última página contendo uma pesquisa geral, onde o usuário entra com um nome de barco e o sistema busca na API referências desse veículo, filtrando antes da exibição se ele é pesqueiro ou
  não e retornando ao usuário referências que podem ser utilizadas para a inserção no mapa individual dele.</p>
</div>

## Desafios e Melhorias

Acredito que para uma versão inicial o app está bem coeso e funcional mas acrescentaria como pontos a serem melhorados: 
- Otimização do código;
- Velocidade de processamento dos dados colhidos;
- Documentação;
- Melhoria visual (tanto do mapa quanto da página).

Algumas coisas tentei implementar como a parte de carregamento assíncrono, algo que nunca tinha visto anteriormente, que me serviu de aprendizado, porém devo levar em consideração os pontos acima para próximas versões. 
