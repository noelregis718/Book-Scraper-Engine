import re

with open('docs/apps_script_drafter.js', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace getBody placeholders
content = content.replace('[Insert Duration Produced]', '${argus.duration}')
content = content.replace('[Insert LDAUs]', '${argus.ldau}')
content = content.replace('[Insert Number of Comments]', '${argus.comments}')
content = content.replace('[Insert Ratings]', '${argus.ratings}')
content = content.replace('[Insert Reviews]', '${argus.reviews}')
content = content.replace('[Insert Listening Hours]', '${argus.hours}')

# Add argus to loop
var_block = """    let email = row[emailCol];
    let showId = showIdCol > -1 ? row[showIdCol] : "";
    let argus = (showId && argusData[showId.toString().trim()]) ? argusData[showId.toString().trim()] : {duration: "[Insert Duration Produced]", ldau: "[Insert LDAUs]", comments: "[Insert Number of Comments]", ratings: "[Insert Ratings]", reviews: "[Insert Reviews]", hours: "[Insert Listening Hours]"};"""
content = content.replace('    let email = row[emailCol];', var_block)

# Replace all createDraft calls in the main loop to include argus
content = content.replace(', revLink);', ', revLink, argus);')

with open('docs/apps_script_drafter.js', 'w', encoding='utf-8') as f:
    f.write(content)
