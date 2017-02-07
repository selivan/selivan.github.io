## Выбор софта

Зачем вообще нужен syslog-сервер, когда есть elastic beats, logstash, systemd-journal-remote и ещё много новых блестящих технологий?

- Это стандарт для ведения логов в POSIX-совместимых системах.  
Некоторый софт, например haproxy, использует только его. То есть совсем избавится от syslog вам всё равно не удастся
- Его использует сетевое железо
- Сложнее в настройке, но богаче по возможностям, чем альтернативные решения.
Например, Elastic Filebeat до сих пор не умеет inotify.
- Нетребователен к памяти. Возможно использование на embedded системах после [небольшого тюнинга](http://wiki.rsyslog.com/index.php/Reducing_memory_usage).
- Позволяет фильтровать сообщение перед сохранением/пересылкой.  
Странная задача, но иногда требуется. Например, [PCI DSS](https://ru.wikipedia.org/wiki/PCI_DSS) в разделе 3.4 требует маскировать или шифровать номера карт, если они сохраняются на диск. Тонкость в том, что если кто-то ввёл номер карты в строку поиска или в форму обратной связи, то как только вы сохранили запрос в лог, вы нарушаете стандарт.

*Наблюдение*: пользователи пытаются ввести номер карты в любое поле ввода на странице, и норовят сообщить его саппорту вместе с CVV и PIN.

<cut />

## Формат сообщений и legacy

*TLDR*: всё плохо.

Syslog появился в 80-х, и быстро стал стандартом логирования для Unix-like систем и сетевого оборудования. Стандарта не было, все писали по принципу совместимости с существующим софтом. В 2001 IETF описал текущее положение вещей в RFC 3164(статус "informational"). Т. к. реализации очень отличаются, то в частности в этом документе сказано "содержание любого IP пакета отправленного на UDP порт 514 должно рассматриваться как сообщение syslog". Потом попробовали стандартизировать формат в RFC 3195, но документ получился неудачным, для него в данный момент нету ни одной живой реализации. В 2009 приняли RFC 5424, определяющий структурированные сообщения, но этим редко кто пользуется.

[Вот тут](http://www.rsyslog.com/doc/syslog_parsing.html) можно прочитать, что обо всём этом думает автор rsyslog Рейнер Герхард(Rainer Gerhards). Фактически, по-прежнему все реализуют syslog как попало, и задача интерпретировать всё это разнообразие ложиться на syslog-сервер. Например, в rsyslog включен [специальный модуль](http://www.rsyslog.com/doc/v8-stable/configuration/modules/pmciscoios.html) для разбора формата, используемого CISCO IOS, ну и для самых плохих случаев начиная с пятой версии можно определять собственные парсеры.

Сообщения syslog при передаче по сети выглядят примерно так:

```
<PRI> TIMESTAMP HOST TAG MSG
```

- `PRI` - Priority. Вычисляется как `facility * 8 + severity`.
  - Facility(категория) принимает значения от 0 до 23, им соответствуют различные категории системных служб: 0 - kernel, 2 - mail, 7 - news. Последние 8 - от local0 до local7 - определены для служб, не попадающих в предопределённые категории. [Полный список](https://en.wikipedia.org/wiki/Syslog#Facility).
  - Severity(важность) принимает значения от 0(emergency, самая высокая) до 7(debug, самая низкая). [Полный список](https://en.wikipedia.org/wiki/Syslog#Severity_level).
- `TIMESTAMP` - время, обычно в формате "Feb  6 18:45:01". Согласно RFC 3164, может записываться в формате времени ISO 8601: "2017-02-06T18:45:01.519832+03:00" с большей точностью и с учётом используемой временной зоны.
- `HOST` - имя хоста, сгенерировавшего сообщение
- `TAG` - содержит имя программы, сгенерировавшей сообщение.  Не более 32 алфавитно-цифровых символов, хотя по факту многие реализации позволяют больше. Любой не-алфавитноцифровой символ заканчивает TAG и начинает MSG, обычно используется двоеточие. Иногда в квадратных скобках содержит номер сгенерироваашего сообщение процесса. Т. к. `[ ]` - не алфавитно-цифровые символы, то номер процесса вместе с ними должен считаться частью сообщения. Но обычно все реализации считают это частью тега, считая сообщением всё после символов ": "
- `MSG` - сообщение. Из-за неопределённости с тем, где же кончается тег и начинается сообщение, в начало может приклеивается пробел. Не может содержать символов перевода строки: они являются разделителями фреймов, и начнут новое сообщение. Способы всё же переслать multi-line сообщение:
    - экранирование. Получим на стороне приёмника текст с `#012` вместо переводов строки
    - использование octet-counted TCP Framing, как определено в RFC 5425 для TLS-enabled syslog. Нестандарт, только некоторые реализации.

#### Альтернатива: RELP

Если сообщения пересылаются между хостами, использующими rsyslog, можно вместо plain TCP sysog использовать [RELP](http://www.rsyslog.com/doc/relp.html) - Reliable Event Logging Protocol. Был создан для rsyslog, сейчас поддерживается и некоторыми другими системами. В частности, его понимают Logstash и Graylog. Для транспорта использует TCP. Может опционально шифровать сообщения с помощью TLS. Надёжнее plain TCP, т. к. имеет подтверждение доставки сообщений. Решает проблему с multi-line сообщениями.

## Конфигурация rsyslog

В отличии от второй распространённой альтернативы, syslog-ng, rsyslog совместим с конфигами исторического syslogd:

```bash
auth,authpriv.*            /var/log/auth.log
*.*;auth,authpriv.none     /var/log/syslog
*.*       @syslog.example.net
```

Т. к. возможности rsyslog гораздо больше, чем у его предшественника, формат конфигов был расширен дополнительными директивами, начинающимися со знака `$`:

```bash
$ActionFileDefaultTemplate RSYSLOG_TraditionalFileFormat
$WorkDirectory /var/spool/rsyslog
$IncludeConfig /etc/rsyslog.d/*.conf
```

Начиная с шестой версии, появился си-подобный формат RainerScript, позволяющий задавать сложные правила обработки сообщений.

Т. к. всё это делалось постепенно и с учётом совместимости со старыми конфигами, то в итоге получилась пара неприятных моментов:
- некоторые плагины(я пока с такими не сталкивался) могут не поддерживать новый RainerScript стиль настроек, им по-прежнему нужны старые директивы
- настройка через старые директивы не всегда работает как ожидается для нового формата:
    - если модуль `omfile` вызывается с помощью старого формата: `auth,authpriv.*  /var/log/auth.log`, то владелец и разрешения получившегося файла регулируются старыми директивами `$FileOwner`, `$FileGroup`, `$FileCreateMode`. А вот если он вызывается с помощью `action(type="omfile" ...)`, то эти директивы игнорируются, и надо настраивать параметы action или задавать при загрузке модуля
    - Директивы вида `$ActionQueueXXX` настраивают только ту очередь, которая будет использована в первом action после них, потом значения сбрасываются.
- точки с запятой где-то запрещены, а где-то наоборот обязательны(второе реже)

Чтобы не спотыкаться об эти тонкости(да, в документации они описаны, но кто же её целиком читает?), стоит следовать простым правилам:
- для маленьких простых конфигов использовать старый формат:  `:programname, startswith, "haproxy"  /var/log/haproxy.log`
- для сложной обработки сообщений и для тонкой настройки Actions всегда использовать RainerScript, не трогая legacy директивы вида `$DoSomething`

Подробнее про формат конфига [здесь](http://www.rsyslog.com/doc/v8-stable/configuration/basic_structure.html#configuration-file).

## Обработка сообщений
- Все сообщения приходят из одного из Inputs и попадают на обработку в привязанный к нему RuleSet. Если это явно не задано, то сообщения попадут в RuleSet по-умолчанию. Все директивы обработки сообщений, не вынесенные в отдельные RuleSet-блоки, относятся именно к нему. В частности, к нему относятся все директивы из традиционного формата конфигов:  
 `local7.*  /var/log/myapp/my.log`
- к Input привязан список парсеров для разбора сообщения. Если явно не задано, будет использоваться список парсеров для разбора традиционного формата syslog
- Парсер выделяет из сообщения свойства. Самые используемые:
    - `$msg` - сообщение
    - `$rawmsg` - сообщение целиком до обработки парсером
    - `$fromhost`, `$fromhost-ip` - DNS имя и IP адрес хоста-отправителя
    - `$syslogfacility`, `$syslogfacility-text` - facility в числовой и текстовой форме
    - `$syslogseverity`, `$syslogseverity-text` - то же для severity
    - `$timereported` - время из сообщения
    - `$syslogtag` - поле TAG
    - `$programname` - поле TAG с отрезанным id процесса: `named[12345]` -> `named`
    - весь список можно посмотреть [тут](http://www.rsyslog.com/doc/v8-stable/configuration/properties.html)
- RuleSet содержит список правил, правило состоит из фильтра и привязанных к одного или нескольких Actions
- Фильтры - логические выражения, с использованием свойств сообщения. [Подробнее про фильтры](http://www.rsyslog.com/doc/v8-stable/configuration/filters.html)
- Правила применяются последовательно к сообщению, попавшему в RuleSet, на первом сработавшем правиле сообщение не останавливается
- Чтобы остановить обработку сообщения, можно использовать специальное discard action: `stop` или `~` в легаси-формате.
- Внутри Action часто используются шаблоны. Шаблоны позволяют генерировать данные для передачи в Action из свойств сообщения, например, формат сообщения для передачи по сети или имя файла для записи. [Подробнее про шаблоны](http://www.rsyslog.com/doc/v8-stable/configuration/templates.html)
- Как правило, Action использует модуль вывода("om...") или модуль изменения сообщения("mm..."). Вот некоторые из них:
    - [omfile](http://www.rsyslog.com/doc/v8-stable/configuration/modules/omfile.html) - вывод в файл
    - [omfwd](http://www.rsyslog.com/doc/v8-stable/configuration/modules/omfwd.html) - пересылка по сети, через udp или tcp
    - [omrelp](http://www.rsyslog.com/doc/v8-stable/configuration/modules/omrelp.html) - пересылка по сети по протоколу RELP
    - [onmysql](http://www.rsyslog.com/doc/v8-stable/configuration/modules/ommysql.html), [ompgsql](http://www.rsyslog.com/doc/v8-stable/configuration/modules/ompgsql.html), [omoracle](http://www.rsyslog.com/doc/v8-stable/configuration/modules/omoracle.html) - запись в базу
    - [omelasticsearch](http://www.rsyslog.com/doc/v8-stable/configuration/modules/omelasticsearch.html) - запись в ElasticSearch
    - [omamqp1](http://www.rsyslog.com/doc/v8-stable/configuration/modules/omamqp1.html) - пересылка по протоколу AMQP 1.0
    - [весь список](http://www.rsyslog.com/doc/v8-stable/configuration/modules/idx_output.html) модулей вывода

[Подробнее про порядок обработки сообщений](http://www.rsyslog.com/doc/v8-stable/configuration/basic_structure.html#quick-overview-of-message-flow-and-objects).

## Примеры конфигурации

Записываем все сообщения категорий auth и authpriv в файл `/var/log/auth.log`, и продолжаем их обработку:

```
# legacy
auth,authpriv.*  /var/log/auth.log
# новый формат
if ( $syslogfacility-text == "auth" or $syslogfacility-text == "authpriv" ) then {
    action(type="omfile" file="/var/log/auth.log")
}
```

Все сообщения с именем программы, начинающимся с "haproxy", записываем в файл `/var/log/haproxy.log`, не сбрасывая буфер на диск после записи каждого сообщения, и прекращаем дальнейшую обработку:

```
# legacy
:programname, startswith, "haproxy", -/var/log/haproxy.log
& ~
# новый формат
if ( $programname startswith "haproxy" ) then {
    action(type="omfile" file="/var/log/haproxy.log" flushOnTXEnd="off")
    stop
}
# можно совмещать
if $programname startswith "haproxy" then -/var/log/haproxy.log
&~
```

Проверка конфига: `rsyslogd -N 1`. Больше примеров конфигурации: [раз](http://www.rsyslog.com/doc/v8-stable/configuration/examples.html), [два](http://wiki.rsyslog.com/index.php/Configuration_Samples).

## Клиент: пересылка логов с сохранением имени файла

Сохранять имена файлов мы будем в поле `TAG`. В имена хочется включить каталоги, чтобы не наблюдать одноуровневую россыпь файлов: `haproxy/error.log`. Если лог читается не из файла, а из переданных в syslog сообщений от программы, то она может не согласиться записывать в TAG символ `/`, потому что это не соответствует стандарту. Поэтому мы закодируем их двойными подчеркиваниями, а на лог-сервере распарсим обратно.

Создадим шаблон для передачи логов по сети. Мы хотим передавать сообщения с тегами длиннее 32 символов(у нас длинные названия логов), и передавать более точную, чем стандартную, метку времени с указанием временной зоны. Кроме того, к названию лог-файла будет добавлена локальная переменная `$.suffix`, позже станет понятно, зачем. Локальные переменные в RainerScript начинаются с точки. Если переменная не определена, она раскроется в пустую строку.

```bash
template (name="LongTagForwardFormat" type="string"
string="<%PRI%>%TIMESTAMP:::date-rfc3339% %HOSTNAME% %syslogtag%%$.suffix%%msg:::sp-if-no-1st-sp%%msg%")
```

Теперь создадим RuleSet, который будут использоваться для передачи логов по сети. Его можно будет присоединять к Input, читающим файлы, или вызывать как функцию. Да, rsyslog позволяет вызвать один RuleSet из другого. Для использования RELP надо сначала загрузить соответствующий модуль.

```bash
# http://www.rsyslog.com/doc/relp.html
module(load="omrelp")

ruleset(name="sendToLogserver") {
    action(type="omrelp" Target="syslog.example.net" Port="20514" Template="LongTagForwardFormat")
}
```

Теперь создадим Input, читающий лог-файл, и присоединим к нему этот RuleSet.

```bash
input(type="imfile"
	File="/var/log/myapp/my.log"
	Tag="myapp/my.log"
	Ruleset="sendToLogserver")
```

Стоит обратить внимание, что для каждого считываемого файла rsyslog создаёт state-файлы в своём рабочем каталоге(задаётся директивой `$WorkDirectory`). Если rsyslog не может создавать там файлы, то весь лог-файл будет заново передаваться после перезапуска rsyslog.

В случае, если какое-то приложение пишет в общий syslog с определённым тегом, и мы хотим как сохранять это в файл, так и пересылать по сети:

```
# Template to output only message
template(name="OnlyMsg" type="string" string="%msg:::drop-last-lf%\n")

if( $syslogtag == 'nginx__access:')  then {
    # write to file
    action(type="omfile" file="/var/log/nginx/access" template="OnlyMsg")
    # forward over network
    call sendToLogserver
    stop
}
```

Последний `stop` нужен, чтобы прекратить обрабатывать эти сообщения, иначе они попадут в общий syslog. Кстати, если приложение умеет выбирать другой unix socket для syslog, кроме стандартного `/dev/log`(nginx и haproxy так умеют), то можно с помощью модуля [imuxsock](http://www.rsyslog.com/doc/v8-stable/configuration/modules/imuxsock.html) сделать для этого сокета отдельный Input и прицепить к нему нужный RuleSet, не разбирая логи из общего потока по тегам.

#### Чтение лог-файлов, заданных через wildcard

*Интерлюдия*

Программист: Не могу найти на лог-сервере логи somevendor.log за начало прошлого месяца, посмотри плиз  
Девопс: Эээ... а мы разве пишем такие логи? Предупреждать же надо. Ну в любом случае всё старше недели логротейт потёр, если мы его не сохраняли - значит уже нету.  
Программист: *бурно возмущается*  

Если приложение пишет много разных логов, и иногда появляются новые, то обновлять конфиги каждый раз неудобно. Хочется это автоматизировать. Модуль [imfile](http://www.rsyslog.com/doc/v8-stable/configuration/modules/imfile.html) умеет считывать файлы, заданные вайлдкардом, и сохранять в мета-данных сообщения путь к файлу. Правда, путь сохраняется полный, а нам нужен только последний компонент, который оттуда придётся добыть. Кстати, тут нам и пригодится переменная `$.suffix`

```bash
input(type="imfile"
    File="/srv/myapp/logs/*.log"
	Tag="myapp__"
	Ruleset="myapp_logs"
	addMetadata="on")

ruleset(name="myapp_logs") {
    # http://www.rsyslog.com/doc/v8-stable/rainerscript/functions.html
	# re_extract(expr, re, match, submatch, no-found)
	set $.suffix=re_extract($!metadata!filename, "(.*)/([^/]*)", 0, 2, "all.log");
	call sendToLogserver
}
```

Вайлдкарды поддерживаются только в режиме работы imfile `inotify`(это режим по-умолчанию).

#### Multiline лог-файлы

Для работы с multi-line лог-файлами модуль imfile предлагает три варианта:
- `readMode=1` - сообщения разделены пустой строкой
- `readMode=2` - новые сообщения начинаются с начала строки, продолжение сообщения идёт с отступом. Часто так выглядят стектрейсы
- `startmsg.regex` - определять начало нового сообщения по regexp(POSIX Extended)

Первые два варианта имеют проблемы в режиме работы `inotify`, и при необходимости третий легко их заменяет с соответствующим regexp. Считывание multi-line логов имеет одну тонкость. Обычно признак нового сообщения находится в его начале, и мы не можем быть уверены, что программа закончила писать прошлое сообщение, пока не началось следующее. Из-за этого последнее сообщение может никогда не передаваться. Чтобы этого избежать, мы задаём `readTimeout`, по истечении которого сообщение считается законченным и будет передано.

```bash
input(type="imfile"
    File="/var/log/mysql/mysql-slow.log"
    # http://blog.gerhards.net/2013/09/imfile-multi-line-messages.html
    startmsg.regex="^# Time: [0-9]{6}"
    readTimeout="2"
    # no need to escape new line for RELP
    escapeLF="off"
    Tag=" mysql__slow.log"
    Ruleset="sendToLogserver")
```

## Сервер

На сервере надо принять переданные логи и разложить их по папкам, в соответствии с IP передающего хоста и временем отправления: `/srv/log/192.168.0.1/2017-02-06/myapp/my.log`. Для того, чтобы задать имя лог-файла в зависимости от содержания сообщения, мы также можем использовать шаблоны. Переменную `$.logpath` нужно будет задать внутри RuleSet перед использованием шаблона.

```bash
template(name="RemoteLogSavePath" type="list") {
    constant(value="/srv/log/")
    property(name="fromhost-ip")
    constant(value="/")
    property(name="timegenerated" dateFormat="year")
    constant(value="-")
    property(name="timegenerated" dateFormat="month")
    constant(value="-")
    property(name="timegenerated" dateFormat="day")
    constant(value="/")
    property(name="$.logpath" )
}
```

Загрузим нужные модули и выключим `$EscapeControlCharactersOnReceive`, иначе в принятых логах все переводы строки заменятся на `\n`

```bash
# Accept RELP messages from network
module(load="imrelp")
input(type="imrelp" port="20514" ruleset="RemoteLogProcess")

# Default parameters for file output. Old-style global settings are not working with new-style actions
module(load="builtin:omfile" FileOwner="syslog" FileGroup="adm" dirOwner="syslog"
        dirGroup="adm" FileCreateMode="0640" DirCreateMode="0755")

# Module to remove 1st space from message
module(load="mmrm1stspace")

# http://www.rsyslog.com/doc/v8-stable/configuration/input_directives/rsconf1_escapecontrolcharactersonreceive.html
# Print recieved LF as-it-is, not like '\n'. For multi-line messages
# Default: on
$EscapeControlCharactersOnReceive off
```

Теперь создадим RuleSet, разбирающий прилетевшие логи и раскладывающий их по папкам. Службы, полагающиеся для логирования исключительно на syslog, ожидают, что он сохранит время сообщения. Поэтому логи, прилетевшие со стандартными facility, мы будем сохранять в формате syslog, а для прилетевших с facility local0-local7 будем вынимать имя лога из  поля `TAG`, и записывать только само сообщение без остальных полей syslog. Проблема с приклеенным к сообщению пробелом остаётся для RELP, потому что возникает ещё на этапе разбора сообщений, мы будем этот пробел отрезать.

Для увеличения производительности будем писать асинхронно: `asyncWriting="on"` и с большим буфером `ioBufferSize=64k`. Не будем сбрасывать буфер после каждого полученного сообщения `flushOnTXEnd="off"`, но будем это делать каждую секунду, чтобы логи появлялись на лог-сервере достаточно оперативно: `flushInterval="1"`.

```
ruleset(name="RemoteLogProcess") {
    # For facilities local0-7 set log filename from $programname field: replace __ with /
    # Message has arbitary format, syslog fields are not used
    if ( $syslogfacility >= 16 ) then
    {
        # Remove 1st space from message. Syslog protocol legacy
        action(type="mmrm1stspace")

        set $.logpath = replace($programname, "__", "/");
        action(type="omfile" dynaFileCacheSize="1024" dynaFile="RemoteLogSavePath" template="OnlyMsg"
        flushOnTXEnd="off" asyncWriting="on" flushInterval="1" ioBufferSize="64k")

    # Logs with filename defined from facility
    # Message has syslog format, syslog fields are used
    } else {
        if (($syslogfacility == 0)) then {
    	    set $.logpath = "kern";
        } else if (($syslogfacility == 4) or ($syslogfacility == 10)) then {
            set $.logpath = "auth";
        } else if (($syslogfacility == 9) or ($syslogfacility == 15)) then {
            set $.logpath = "cron";
        } else {
            set $.logpath ="syslog";
        }
        # Built-in template RSYSLOG_FileFormat: High-precision timestamps and timezone information
        action(type="omfile" dynaFileCacheSize="1024" dynaFile="RemoteLogSavePath" template="RSYSLOG_FileFormat"
        flushOnTXEnd="off" asyncWriting="on" flushInterval="1" ioBufferSize="64k")
    }
} # ruleset
```

## Надёжная доставка сообщений. Очереди

Для некоторых Actions выполнение тормозить или приостанавливаться, например пересылка логов по сети или запись в базу. Чтобы не терять сообщение и не мешать работать следующим Actions, можно использовать [очереди](http://www.rsyslog.com/doc/v8-stable/concepts/queues.html). Каждому Action всегда сопоставлена очередь сообщений, по умолчанию это Direct Queue нулевого размера. Ещё есть основная очередь для поступивших из всех Input сообщений, её тоже можно настраивать.

Виды очередей: дисковые, in-memory, и самый интересный вариант- комбинированный: Disk-Assisted Memory Queues. Такие очереди используют память и начинают использовать диск, если очередь в памяти переполняется, или надо сохранить неотправленные сообщения на время перезагрузки сервиса. Сообщения начнут записываться на диск, когда количество сообщений в очереди достигнет `queue.highwatermark`, и пререстанут сохраняться на диск, когда их количество упадёт до `queue.lowwatermark`. Чтобы неотправленные сообщения сохранялись на диск во время презагрузки сервиса, надо указать `queue.saveonshutdown="on"`.

Если персылка логов по сети или запись в базу была неуспешной, Action приостанавливается. rsyslog пытается возобновить работу Action через определённые, увеличивающиеся с каждой попыткой интервалы времени. Чтобы логи начали пересылаться вскоре после решения проблем, надо выставить  `action.resumeRetryCount="-1"` (неограниченный) и интервал для остановки очереди поменьше: `action.resumeInterval="10"`. Подробнее про [параметры Actions](http://www.rsyslog.com/doc/v8-stable/configuration/actions.html).

RuleSet на клиенте с очередью будет выглядеть так:

```bash
ruleset(name="sendToLogserver") {
    # Queue: http://www.rsyslog.com/doc/v8-stable/concepts/queues.html#disk-assisted-memory-queues
    # Disk-Assisted Memory Queue: queue.type="LinkedList" + queue.filename
    # queue.size - max elements in memory
    # queue.highwatermark - when to start saving to disk
    # queue.lowwatermark - when to stop saving to disk
    # queue.saveonshutdown - save on disk between rsyslog shutdown
    # action.resumeRetryCount - number of retries for action, -1 = eternal
    # action.resumeInterval - interval to suspend action if destination can not be connected
    # After each 10 retries, the interval is extended: (numRetries / 10 + 1) * Action.ResumeInterval
    action(type="omrelp" Target="syslog.example.net" Port="20514" Template="LongTagForwardFormat"
    queue.type="LinkedList" queue.size="10000" queue.filename="q_sendToLogserver" queue.highwatermark="9000"
    queue.lowwatermark="50" queue.maxdiskspace="500m" queue.saveonshutdown="on" action.resumeRetryCount="-1"
    action.reportSuspension="on" action.reportSuspensionContinuation="on" action.resumeInterval="10")
}
```

Теперь можно спокойно перезугружать лог-сервер - сообщения созраняться в очереди и будут переданы, когда он станет доступен.

## Отказоустойчивость

Можно настроить Action для выполнения только в случае, если предыдущее Action было приостановлено: [описание](http://www.rsyslog.com/action-execonlywhenpreviousissuspended-preciseness/). Это позволяет настраивать failover конфигурации. Некоторые Actions используют транзакции для увеличения производительности. В таком случае, успех или неудача будут известны только после завершения транзакции, когда сообщения уже обработаны. Это может приводить к потере части сообщений без вызова failover Action. Чтобы такого не происходило, надо ставить параметр `queue.dequeuebatchsize="1"`(по-умолчанию 16), что может снизить производительность.

```bash
ruleset(name="sendToLogserver") {
    action(type="omrelp" Target="syslog1.example.net" Port="20514" Template="LongTagForwardFormat")
    action(type="omrelp" Target="syslog2.example.net" Port="20514" Template="LongTagForwardFormat"
    action.execOnlyWhenPreviousIsSuspended="on" queue.dequeuebatchsize="1")
}
```

Эту возможность я пока не пробовал в продакшене.

## Заключение

Описанная в статье конфигурация работает для rsyslog v8, на более ранних версиях не проверялась. Для Ubuntu есть официальный ppa [adiscon/v8-stable](https://launchpad.net/~adiscon/+archive/ubuntu/v8-stable). Для CentOS/RHEL можно использовать [официальный репозиторий](http://www.rsyslog.com/rhelcentos-rpms/).
