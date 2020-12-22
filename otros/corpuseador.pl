
use strict;
print("\n");

my @corpus;
my $ntotal_enunciados;
my $ncorpus;
my @corpus;

my $dir = "/Users/r66y/documents/wget";

opendir (DIR, $dir) || die "\n\nno puedo abrir $dir\n\n";

my @dir = readdir(DIR);

closedir(DIR);

foreach my $archivo(@dir)
{
##	print($archivo);
##	print("\n");
	if ($archivo =~ /.html/)
	{
		print("\n\n\n\n");
		print("abriendo archivo $archivo...\n");
		open(FILE, "<", $archivo) or warn "\nno puedo abrir el fichero $archivo\n\n";
		my @archivo = <FILE>;
		close FILE;
##		print("ok\nagregando al corpus...\n");
		
		my $nenunciados;
		my @nelementos;
		my $nelementos;
	
		foreach my $line (@archivo) 
		{	
	
			if ($line =~ /<p>/ or $line =~ /<br\/>/)
			{
				$nenunciados++;
				$line =~ s/<p>|li>|\/li>|<\/p>|&quot;|<strong>|<\/strong>|<br>|<br\/>//g;
				$line =~ s/div class=".+">//g;
				$line =~ s/<<iframe.+<\/iframe><\/div>//g;
				$line =~ s/<a href=".+<\/a>//g;
				$line =~ s/<<?img src=".+alt=""\/>//g;
				$line =~ s/http.+<\/a>//g;
				$line =~ s/<<\/a><\/div>//g;
				$line =~ s/<//g; 
				@nelementos = split(/ /, $line);
				$nelementos = @nelementos + $nelementos;	
				print "\n$line";								
			}
		}
	
##		print "archivo $archivo agregado al corpus\n";
##		print "número de filas leídas: $nfilas\n";
##		print "número de elementos agregados: $nelementos\n\n";
		
		$ntotal_enunciados = $ntotal_enunciados + $nenunciados;	
		@corpus = @corpus + @nelementos;
		$ncorpus = $ncorpus + $nelementos;
	
	}
}

print "\n\n";
print "número total de enunciados leídos: $ntotal_enunciados\n";
print "número total de elementos en el corpus: $ncorpus\n";

print("\n")
