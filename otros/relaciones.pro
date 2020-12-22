:- style_check(-singleton).

% casos conocidos para distintas obras de ciencia ficcion: 
% obra(nombre,autor,formato,antecedente,año)

obra(akira,otomo,novela_grafica,o,1982).
obra(pesadillas,otomo,novela_grafica,o,1983).
obra(metropolis_manga,tezuka,manga,metropolis,1949).
obra(paprika,tsutsui,novela,o,1993).
obra(dune,herbert,novela,o,1965).
obra(i_robot,asimov,novela,o,1950).
obra(perfect_blue_complete_metamorfosis,takeuchi,novela,o,1991).
obra(do_androids_dream_of_electric_sheep,dick,novela,o,1968).
obra(the_minority_report,dick,cuento,o,1956).
obra(v_for_vendetta,moore,comic,o,1982).
obra(sherlock_holmes,conan_doyle,novela,o,1887).
obra(case_closed,aoyama,manga,cuentos_de_misterio,1994).
obra(cuentos_de_misterio,ranpo,cuento,sherlock_holmes,1930).
obra(magnetic_rose,kon,guion,o,1994).
obra(astro_boy,tezuka,manga,o,1952).
obra(buddha_el_gran_viaje,tezuka,manga,o,1972).
obra(panorama_island,ranpo,novela,o,1926).
obra(the_strange_tale_of_panorama_island,maruo,novela_grafica,panorama_island,2008).
obra(enders_game,scott_card,novela,o,1985).
obra(xenosaga_the_manga,baba,manga,xenosaga,2006).
obra(neuromancer,gibson,novela,o,1984).
obra(johny_mnemonic,gibson,cuento,o,1981).
obra(ghost_in_the_shell,shirow,manga,o,1989).
obra(mistery_dungeons,torenko,novel,dragon_quest,1995).
obra(sherlock_holmes_film,ritchie,pelicula,sherlock_holmes,2009).
obra(la_jetee,marker,corto,hitchckok,1962).
obra(twelve_monkeys,gilliam,pelicula,la_jetee,1996).
obra(detective_conan,yomiuri,serie_anime,case_closed,1996).
obra(detective_conan_skycraper_timer,kodama,pelicula_anime,case_closed,1997).
obra(paprika_dream_detective,kon,pelicula_anime,paprika,2006).
obra(perfect_blue,kon,pelicula_anime,perfect_blue_complete_metamorfosis,1997).
obra(akira_film,otomo,pelicula_anime,akira,1988).
obra(inception,nolan,pelicula,paprika_dream_detective,2010).
obra(looper,johnson,pelicula,pesadillas,2012).
obra(black_swan,aronofsky,pelicula,perfect_blue,2010).
obra(i_robot_film,proyas,pelicula,i_robot,2004).
obra(dune_film,lynch,pelicula,dune,1984).
obra(metropolis,lang,pelicula,o,1927).
obra(tetsukas_metropolis,rintaro,pelicula,metropolis_manga,2001).
obra(blade_runner,scott,pelicula,do_androids_dream_of_electric_sheep,1982).
obra(minority_report,spielberg,pelicula,the_minority_report,2002).
obra(dark_city,proyas,pelicula,lost_highway,1998).
obra(matrix,wachowski,pelicula,dark_city,1999).
obra(v_for_vendetta_film,wachowski,pelicula,v_for_vendetta,2002).
obra(animatrix_II,morimoto,pelicula_anime,matrix,2003).
obra(magnetic_rose,morimoto,corto,o,1995).
obra(final_fantasy_unlimited,maeda,serie_anime,final_fantasy,2001).
obra(animatrix_III,maeda,pelicula_anime,matrix,2003).
obra(evangelion,anno,serie,o,1995).
obra(evangelion_3,maeda,pelicula_anime,evangelion,2012).
obra(final_fantasy_legend_of_the_crystals,rintaro,pelicula_anime,final_fantasy,1994).
obra(astro_boy_film,bowers,pelicula,astro_boy,2009).
obra(steam_boy,otomo,pelicula_anime,astro_boy,2004).
obra(buddha,morishita,pelicula_anime,buddha_el_gran_viaje,2011).
obra(dragon_quest_serie,rintaro,serie,dragon_quest,1989).
obra(prometheus,scott,pelicula,alien,2012).
obra(lost_highway,lynch,pelicula,o,1997).
obra(alien,scott,pelicula,o,1979).
obra(benders_game,groening,pelicula_anime,enders_game,2012).
obra(xenosaga_the_animation,asahi,serie,xenosaga,2008).
obra(tron,lisberger,pelicula,o,1982).
obra(tron_legacy,kosinski,pelicula,tron,2010).
obra(johnny_mnemonic,longo,pelicula,johny_mnemonic,1995).
obra(ghost_in_the_shell,oshii,pelicula_anime,ghost_in_the_shell_manga,1995).
obra(final_fantasy,sakaguchi,rpg,o,1987).
obra(dune_videojuego,cryo,rpg,dune,1992).
obra(astro_boy_omega_factor,konami,arcade,astro_boy,2004).
obra(astro_boy_the_game,imagi,arcade,astro_boy,1988).
obra(dragon_quest,enix,arcade,o,1986).
obra(metroid,nintendo,arcade,alien,1986).
obra(case_closed_miriapolis_investigation,marvelous,rpg,case_closed,2010).
obra(chrono_trigger,square,rpg,o,1995).
obra(chrono_cross,square_enix,rpg,chrono_trigger,1998).
obra(xenogears,takahashi,rpg,o,1998).
obra(xenosaga,takahashi,rpg,xenogears,2002).
obra(xenoblade,takahashi,rpg,xenosaga,2010).
obra(radical_dreamers,square,rpg,chrono_trigger,1996).
obra(neuromancer_cyberpunk_rpg,interplay,rpg,neuromancer,1988).
obra(tron_videogame,bally_midway,arcade,tron,1982).


% reglas para definir autor:
% (autor,obra,formato,antecedente,año)

autor(O,A,F,Y) :- obra(A,O,F,I,Y).


% reglas para la relacion de influencia de una obra a otra:
% “La obra O está basada en OA”
% influencia(obra,obra_anterior,autor,autor_anterior,
% formato,formato_anterior,año_obra,año_obra_anterior):

influencia(O,A,F,Y,OA,AA,FA,YA) :- obra(O,A,F,U,Y),obra(OA,AA,FA,O,YA).


% reglas para la relación de cadena de influencias
% A influenció en AA, AA influenció en AAA:

influencia_cadena(O,A,Y,OA,AA,YA,OAA,AAA,YAA) :- 
influencia(O,A,F,Y,OA,AA,FA,YA),influencia(OA,AA,FA,YA,OAA,AAA,FAA,YAA).


% regla para obras de un mismo autor, se puede ver con obras() de todos modos:

mismo_autor(A,O+F+Y,OA+FA+YA) :- autor(A,O,F,Y),autor(A,OA,FA,YA),O\=OA.





