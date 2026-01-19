tell application "System Events"
    set isSkimRunning to (exists (process "Skim"))
end tell

if isSkimRunning then
    tell application "Skim"
        -- Sauvegarde d'abord tous les PDFs ouverts
        repeat with doc in documents
            if modified of doc then
                save doc
            end if
        end repeat
        
        -- Votre code existant
        set pdfFiles to the file of every document
        repeat with pdfFile in pdfFiles
            set skimFile to (POSIX path of pdfFile)
            set skimFile to text 1 through ((length of skimFile) - 4) of skimFile & ".skim"
            do shell script "if test -f " & quoted form of skimFile & "; then /usr/local/bin/python3 /usr/local/bin/skim_to_text.py " & quoted form of skimFile & "; else echo 'Fichier .skim non trouvé.'; fi"
        end repeat
    end tell
else
    display dialog "Skim n'est pas ouvert !" buttons {"OK"} default button "OK"
end if