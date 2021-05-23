#!/usr/bin/perl

use LWP::UserAgent;
use HTTP::Request::Common qw(POST);
use Time::localtime;

@casts=('Аргентум');
@authors=('Сергей Бунтман', 'Алексей Венедиктов', 'Матвей Ганапольский');


print "Content-type: text/html\n\n";

#Получаем текущую дату
$tm=localtime;
($day, $month, $year)=($tm->mday, $tm->mon,$tm->year);

#Форматируем дату
if($day<10){$day="0".$day}
$month++;
if($month<10){$month="0".$month}
$bigyear=$year+1900;

#Адрес печатной версии программы передач
$ur="http://www.echo.msk.ru/schedule/$bigyear-$month-$day.phtml";

#Скачиваем страничку и бьем на строки
$ua = LWP::UserAgent->new;
$ua->agent("IE :)".$ua->agent);

$res2 = $ua->request(new HTTP::Request('GET' => $ur));
if (!$res2->is_success) {print "Can't get $ur\n";}
@lines=split(/\n/,$res2->content);

#Сейчас будем раздирать ее в клочья
for ($line_num=0; $line_num<=$#lines; $line_num++)
{
 #Ищем "заголовок окошка" и отступаем от него на 3 строчки
 if($lines[$line_num]=~/<!-- Zagolovok okoshka -->/)
 {
  #там между первыми двмя тегами прописано время
  $lines[$line_num+3] =~ />(.{2}):(.{2})</;
  #которое мы помещаем в один массив как текст
  push(@times_txt,"$1:$2");
  #а в другой - как количество минут
  $time=$1*60+$2;
  push(@times,$time);

  #Cчетчик строк
  for($line_in_td=$line_num+9; ;$line_in_td++)
  {
   #Пока не наткнемся на конец ячейки
   if($lines[$line_in_td]=~/<\/td>/){last;}
   #Если наткнулись на конец слоя
   if($lines[$line_in_td]=~/<\/div>/)
   {
     #смотрим не описание ли это ведущих. Если да, то дописываем к предыдущей записи
     if($record=~/Ведущие/)
     {$info[$#info]{author}=$record;$record='';}
     else
      {
       #Если нет, то это называние передачи. Пихаем в массив в виде хэша
       push(@info,{'record'=>$record, 'author'=>''});
       $record='';
      }
   }
   #Чистим строку
   $lines[$line_in_td]=~s/<[^>]*>//gs;
   $lines[$line_in_td]=~s/^\s+//g;
   $lines[$line_in_td]=~s/\s+/ /g;
   chop($lines[$line_in_td]);
   #и компонуем ее
   if($lines[$line_in_td] ne '' && $lines[$line_in_td] ne ','){$record=$record.$lines[$line_in_td];}

  }
 }
}

#Вывод всей программы передач

# for ($record_num=0; $record_num<$#info; $record_num++)
# {
#
#            $length=$times[$record_num+1]-$times[$record_num];
#            $day=$day+$length;
#            print "Время: $times[$record_num], Передача: $info[$record_num]{record} $info[$record_num]{author} Длительность: $length\n";
# }


#Теперь формируем файл настроек UPG


#Заголовок и группы
$setup.="<?xml version=\"1.0\" encoding=\"WINDOWS-1251\"?>\n\n<UPG>\n\n        <Groups>\n";
$setup.="                <Group name='echo'  title='Эхо Москвы'/>\n        </Groups>\n    <Channels>\n\n";

#Перебор полученных записей
for ($record_num=0; $record_num<$#info; $record_num++)
{
      #Ищем название передачи в списке
      foreach $cast(@casts)
      {
         if($info[$record_num]{record}=~/$cast/)
          {
           #Получаем длительность передачи
           $length=$times[$record_num]-$times[$record_num-1];

           #и сохраняем все данные в $setup
           $setup.="<Item name='Код доступа' group=\"echo\">\n";
           $setup.="    <Url>http://ware.catv.ext.ru:8000/moscowecho48.mp3</Url>\n";
           $setup.="    <Directory>$info[$record_num]{record}</Directory>\n";
           $setup.="    <Days>0</Days>\n";
           $setup.="    <Times>$times_txt[$record_num]</Times>\n";
           $setup.="    <Duration>$length</Duration>\n";
           $setup.="</Item>\n";

           #print "Время: $times[$record_num], Передача: $info[$record_num]{record} $info[$record_num]{author} Длительность: $length\n";
          }
      }

      #Все это повторяем для списка ведущих
      foreach $author(@authors)
      {
         if($info[$record_num]{author}=~/$author/)
          {
           $length=$times[$record_num+1]-$times[$record_num];

           $setup.="<Item name='$info[$record_num]{record}' group=\"echo\">\n";
           $setup.="    <Url>http://ware.catv.ext.ru:8000/moscowecho48.mp3</Url>\n";
           $setup.="    <Directory>$info[$record_num]{record}</Directory>\n";
           $setup.="    <Days>0</Days>\n";
           $setup.="    <Times>$times_txt[$record_num]</Times>\n";
           $setup.="    <Duration>$length</Duration>\n";
           $setup.="</Item>\n";

           #print "Время: $times[$record_num], Передача: $info[$record_num]{record} $info[$record_num]{author} Длительность: $length\n";
          }
      }

}

#Окончание настроек
$setup.="\n</Channels>\n\n\n<Settings root=\"Эхо Москвы\" port=\"8282\" ip=\"192.168.0.2\" timeout=\"5\" maxtimeouts=\"7\" maxreconnects=\"10\" />\n</UPG>";

#Скармливаем настройки запущенному UPG
$ua = LWP::UserAgent->new();
$req = POST 'http://127.0.0.1:8282/update.html', ["Setup"=>$setup];
$ua->request($req);