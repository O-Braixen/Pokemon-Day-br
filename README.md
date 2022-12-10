![What Pokémon Day is it today? (python code)](misc/md/header1.png)

Este repositório contém o código usado para executar "**What Pokémon Day is it today?**" no [Twitter](https://twitter.com/WhatPokeDayIsIt) e [Mastodon](https://donphan.social/ @WhatPokeDayIsIt) e Discord! Eu liberei este código-fonte, principalmente para permitir que os usuários executem isso em seu próprio servidor Discord, mas também apenas por diversão! Se você quiser ler sobre como esse código funciona (em termos leigos), verifique [este arquivo MD] (Inner Workings.md)!

Special thanks goes to [PokéAPI](https://pokeapi.co) for providing a lot of the data used here, i.e. Pokémon's names, their National Pokédex numbers, etc!

![Usage](misc/md/header2.png)

Para usar isso, primeiro verifique se você está executando o Python 3.9.9/3.10.x. Python 3.8 *pode* funcionar, mas não foi testado e, portanto, não é suportado; qualquer coisa abaixo de 3,8 não funcionará. Certifique-se de ter o **pip** instalado. Se você planeja usar isso para o Twitter, precisará ter **Acesso Elevado** para a API. Se você quiser usar isso para o Mastodon, certifique-se de que sua instância permite bots e que você pode gerar um!

E se você planeja usar isso para Discord, certifique-se de ter permissões para adicionar bots e apenas siga as [instruções aqui](https://novus.readthedocs.io/en/stable/discord.html); para obter permissões na seção **Convidando seu bot**, basta marcar "*Enviar mensagens*" e "*Ler mensagens/ver canais*" e certifique-se de obter seu *Bot Token*!

Clique [aqui](https://gitlab.com/EeveeEuphoria/pokeday/-/releases/), acesse a versão mais recente e clique em **Download Me! (zip)** para baixar os arquivos necessários. Uma vez feito, extraia-o em algum lugar que você queira acessar facilmente. Em seguida, navegue até o diretório extraído e use `pip install -r requirements.txt` para instalar todos os módulos usados para isso. Se isso não funcionar, use `python3 -m pip install -r requirements.txt`, ou se você estiver no Windows, use `py -3 -m pip install -r requirements.txt`.

**Isto é importante:** dependendo do seu caso de uso para isso, você desejará instalar o pacote pip correspondente. Se você quiser usar isso para *Discord*, use `pip install novus`, para *Mastodon*, use `pip install Mastodon.py` e para *Twitter*, faça `pip install tweepy`. Se esses comandos apresentarem erros, substitua `pip install` por `python3 -m pip install -U`, ou se você estiver no Windows, use `py -3 -m pip install -U`.

Se você planeja usar o script `createcsv.py`, também precisará usar a PokéBase para uso da PokéAPI; basta usar `pip install pokebase`.

Feito isso, execute `main.py` para inicializar o arquivo de configuração usado para isso e para testar se o script realmente funciona. Se tudo correr bem, você deverá ver uma saída como esta: `Arquivo de configuração não encontrado ou corrompido! Gerando um novo e saindo!`

Agora você deve ver um arquivo `config.ini` em sua pasta, abra-o em seu editor de texto favorito. Haverá comentários mostrando como configurar isso a partir daqui!

Quando você executar o script agora, se não houver erros, tada, tudo funcionará! Observe que, se você tiver "Contínuo" definido como falso, precisará executar *manualmente* esse script no momento correto; você não precisa fazer isso, pois o script pode ser executado por conta própria nos momentos corretos, mas se desejar esse controle, você pode fazer isso! O único outro recurso que você perderá é a função automática de retweet/boost que ocorre após 12 horas.

Se você planeja reutilizar o código deste projeto em outra coisa, pode obter seu próprio arquivo .ics no Google Calendars. Vá para as configurações do calendário em questão, role para baixo até **Integrar calendário** e encontre *Endereço público no formato iCal*, você pode usar isso como URL.

Se você quiser personalizar isso para seu próprio uso (ou seja, usos não relacionados a Pokémon), você terá que fazer seu próprio script aqui! Eu ajustei este script especificamente para as complexidades de usar um arquivo de calendário, cheio de datas com títulos como "Sylveon Day #ニンフィアの日", etc. Há muitos comentários no código para explicar como tudo isso funciona!
