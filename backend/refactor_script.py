import re

with open('docs/apps_script_drafter.js', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Extract wrapHtml
wrap_match = re.search(r'(  function wrapHtml\(bodyContent\).*?  \})', content, re.DOTALL)
wrap_html_code = wrap_match.group(1) if wrap_match else ""

# 2. Extract getBody
body_match = re.search(r'(  function getBody\(type, firstName, title, link, grammar, revLink\).*?    \}\n  \})', content, re.DOTALL)
get_body_code = body_match.group(1) if body_match else ""

if wrap_html_code and get_body_code:
    # 3. Remove them from inside processOutreachQueue
    content = content.replace(wrap_html_code, '')
    content = content.replace(get_body_code, '')
    
    # 4. Remove the comment headers inside the function too
    content = content.replace('  // -------------------------------------------------------------\n  // OFFICIAL POCKET FM HTML WRAPPER\n  // -------------------------------------------------------------\n\n', '')
    content = content.replace('  // -------------------------------------------------------------\n  // EMAIL BODIES\n  // -------------------------------------------------------------\n', '')
    
    # 5. Append them to the global scope at the bottom, along with the test function
    test_function = """
// -------------------------------------------------------------
// HELPER FUNCTIONS (MOVED TO GLOBAL SCOPE)
// -------------------------------------------------------------
""" + wrap_html_code.replace('  function', 'function') + "\n\n" + get_body_code.replace('  function', 'function') + """

// -------------------------------------------------------------
// ONE-CLICK TEST GENERATOR (FOR MANAGER REVIEW)
// -------------------------------------------------------------
function testAllTemplates() {
  const email = Session.getActiveUser().getEmail(); // Sends to your own Gmail
  const firstName = "Jane";
  const title = "The Crimson Crown";
  const link = "https://pocketfm.com/show/crimson-crown";
  const revLink = "https://drive.google.com/drive/folders/12345";
  
  const grammar = {
    work: "work", is: "is", has: "has", title: "title", this: "this", it: "it", its: "its"
  };

  const templates = [
    { type: 'welcome', subject: 'Welcome to Pocket FM – here\\'s what happens next' },
    { type: 'vendor', subject: 'Vendor Onboarding Requirements for The Crimson Crown' },
    { type: 'mgInitiated', subject: 'Payment Initiated: Minimum Guarantee for The Crimson Crown' },
    { type: 'mgConfirmed', subject: 'Your Minimum Guarantee Payment Has Been Processed' },
    { type: 'checkIn1', subject: 'We\\'d love your thoughts on The Crimson Crown' },
    { type: 'checkIn2', subject: 'Pocket FM: A quick update on your show: The Crimson Crown' },
    { type: 'launch', subject: '🎉 Your Pocket FM Show Is Now Live' },
    { type: 'revStatement_workedWell_content', subject: 'Pocket FM: An Update on The Crimson Crown' },
    { type: 'revStatement_workedWell_payment', subject: 'Pocket FM: Your earnings are waiting for you!' },
    { type: 'revStatement_didntWorkWell', subject: 'Pocket FM: An Update on The Crimson Crown' },
    { type: 'quarterlyStatements', subject: 'Pocket FM: Quarterly Update for The Crimson Crown' },
    { type: 'eventMixer', subject: 'Save the date: [Event Name]' },
    { type: 'publicNews', subject: 'Latest news from Pocket FM' }
  ];

  let count = 0;
  templates.forEach(t => {
    let bodyContent = getBody(t.type, firstName, title, link, grammar, revLink);
    let wrappedBody = wrapHtml(bodyContent);
    GmailApp.createDraft(email, t.subject, "", { htmlBody: wrappedBody });
    count++;
  });
  
  Logger.log("Successfully generated " + count + " test drafts in your Gmail!");
}
"""
    # Write the modified content back
    with open('docs/apps_script_drafter.js', 'w', encoding='utf-8') as f:
        f.write(content + "\n" + test_function)
        
    print("Refactoring successful. Added testAllTemplates().")
else:
    print("Could not find functions to refactor.")
