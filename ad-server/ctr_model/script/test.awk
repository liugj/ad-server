#!bin/awk -f
BEGIN{
   FS=OFS="\t"
}
{
    split($1,array1," ")
    prob=array1[3]
    split($2,array2," ")
    click=array2[1]
    if (prob>0.06){
        click_sum+=click
        show_sum++
    }
}
END{
    print show_sum,click_sum,click_sum/show_sum
}
