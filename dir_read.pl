#!/usr/bin/perl

# This routine reads directory listing so each filename can be read
sub dir_read 
{
$dir=$_[0];

	opendir(SPECDIR, "$dir");

	@file=readdir(SPECDIR);
   shift(@file);
   shift(@file);

}
1;
