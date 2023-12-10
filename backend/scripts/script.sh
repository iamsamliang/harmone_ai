while read requirement; do
    poetry add "$requirement"
done < requirements.txt
