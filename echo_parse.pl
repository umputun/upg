#!/usr/bin/perl

use LWP::UserAgent;
use HTTP::Request::Common qw(POST);
use Time::localtime;

@casts=('��������');
@authors=('������ �������', '������� ����������', '������ ������������');


print "Content-type: text/html\n\n";

#�������� ������� ����
$tm=localtime;
($day, $month, $year)=($tm->mday, $tm->mon,$tm->year);

#����������� ����
if($day<10){$day="0".$day}
$month++;
if($month<10){$month="0".$month}
$bigyear=$year+1900;

#����� �������� ������ ��������� �������
$ur="http://www.echo.msk.ru/schedule/$bigyear-$month-$day.phtml";

#��������� ��������� � ���� �� ������
$ua = LWP::UserAgent->new;
$ua->agent("IE :)".$ua->agent);

$res2 = $ua->request(new HTTP::Request('GET' => $ur));
if (!$res2->is_success) {print "Can't get $ur\n";}
@lines=split(/\n/,$res2->content);

#������ ����� ��������� �� � ������
for ($line_num=0; $line_num<=$#lines; $line_num++)
{
 #���� "��������� ������" � ��������� �� ���� �� 3 �������
 if($lines[$line_num]=~/<!-- Zagolovok okoshka -->/)
 {
  #��� ����� ������� ���� ������ ��������� �����
  $lines[$line_num+3] =~ />(.{2}):(.{2})</;
  #������� �� �������� � ���� ������ ��� �����
  push(@times_txt,"$1:$2");
  #� � ������ - ��� ���������� �����
  $time=$1*60+$2;
  push(@times,$time);

  #C������ �����
  for($line_in_td=$line_num+9; ;$line_in_td++)
  {
   #���� �� ��������� �� ����� ������
   if($lines[$line_in_td]=~/<\/td>/){last;}
   #���� ���������� �� ����� ����
   if($lines[$line_in_td]=~/<\/div>/)
   {
     #������� �� �������� �� ��� �������. ���� ��, �� ���������� � ���������� ������
     if($record=~/�������/)
     {$info[$#info]{author}=$record;$record='';}
     else
      {
       #���� ���, �� ��� ��������� ��������. ������ � ������ � ���� ����
       push(@info,{'record'=>$record, 'author'=>''});
       $record='';
      }
   }
   #������ ������
   $lines[$line_in_td]=~s/<[^>]*>//gs;
   $lines[$line_in_td]=~s/^\s+//g;
   $lines[$line_in_td]=~s/\s+/ /g;
   chop($lines[$line_in_td]);
   #� ��������� ��
   if($lines[$line_in_td] ne '' && $lines[$line_in_td] ne ','){$record=$record.$lines[$line_in_td];}

  }
 }
}

#����� ���� ��������� �������

# for ($record_num=0; $record_num<$#info; $record_num++)
# {
#
#            $length=$times[$record_num+1]-$times[$record_num];
#            $day=$day+$length;
#            print "�����: $times[$record_num], ��������: $info[$record_num]{record} $info[$record_num]{author} ������������: $length\n";
# }


#������ ��������� ���� �������� UPG


#��������� � ������
$setup.="<?xml version=\"1.0\" encoding=\"WINDOWS-1251\"?>\n\n<UPG>\n\n        <Groups>\n";
$setup.="                <Group name='echo'  title='��� ������'/>\n        </Groups>\n    <Channels>\n\n";

#������� ���������� �������
for ($record_num=0; $record_num<$#info; $record_num++)
{
      #���� �������� �������� � ������
      foreach $cast(@casts)
      {
         if($info[$record_num]{record}=~/$cast/)
          {
           #�������� ������������ ��������
           $length=$times[$record_num]-$times[$record_num-1];

           #� ��������� ��� ������ � $setup
           $setup.="<Item name='��� �������' group=\"echo\">\n";
           $setup.="    <Url>http://ware.catv.ext.ru:8000/moscowecho48.mp3</Url>\n";
           $setup.="    <Directory>$info[$record_num]{record}</Directory>\n";
           $setup.="    <Days>0</Days>\n";
           $setup.="    <Times>$times_txt[$record_num]</Times>\n";
           $setup.="    <Duration>$length</Duration>\n";
           $setup.="</Item>\n";

           #print "�����: $times[$record_num], ��������: $info[$record_num]{record} $info[$record_num]{author} ������������: $length\n";
          }
      }

      #��� ��� ��������� ��� ������ �������
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

           #print "�����: $times[$record_num], ��������: $info[$record_num]{record} $info[$record_num]{author} ������������: $length\n";
          }
      }

}

#��������� ��������
$setup.="\n</Channels>\n\n\n<Settings root=\"��� ������\" port=\"8282\" ip=\"192.168.0.2\" timeout=\"5\" maxtimeouts=\"7\" maxreconnects=\"10\" />\n</UPG>";

#����������� ��������� ����������� UPG
$ua = LWP::UserAgent->new();
$req = POST 'http://127.0.0.1:8282/update.html', ["Setup"=>$setup];
$ua->request($req);