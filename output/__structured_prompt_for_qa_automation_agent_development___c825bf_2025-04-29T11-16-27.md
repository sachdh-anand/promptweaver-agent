# **Structured Prompt for QA Automation Agent Development**  

## **Title**  
**QA Automation Agent for BDD Testing with Playwright**  

## **Objective**  
To create a **CrewAI agent** that automates the generation, execution, and reporting of **BDD-style test cases** using **Playwright**, ensuring **scalability, reliability, and CI/CD integration**.  

## **Context**  
- **CrewAI** is used to build autonomous AI agents for automation.  
- **Playwright** is leveraged for **cross-browser, end-to-end testing**.  
- **BDD (Behavior-Driven Development)** ensures human-readable test cases.  
- **Edge cases** (e.g., authentication, dynamic content) must be covered.  

## **Workflow Steps**  
1. **Input Parsing**  
   - Accept a **valid URL (HTTP/HTTPS)**.  
   - Validate input format (e.g., `https://example.com`).  

2. **BDD Test Case Generation**  
   - Write **Gherkin-style scenarios** (given/when/then).  
   - Include **edge cases** (e.g., invalid login, timeout handling).  

3. **Playwright Test Conversion**  
   - Convert BDD scenarios into **Playwright-compatible JavaScript/TypeScript**.  
   - Use **dynamic selectors** (e.g., `{{SELECTOR}}`).  

4. **Test Execution**  
   - Run tests in **headless mode** (or specified browser).  
   - Support **parallel execution** for scalability.  

5. **Result Reporting**  
   - Generate **JUnit/HTML report**.  
   - Log **pass/fail status** with error details.  

## **Constraints**  
- **Input:** Only **valid URLs** (reject malformed inputs).  
- **Test Coverage:** Must include **authentication, dynamic elements, cross-browser tests**.  
- **CI/CD Compatibility:** Works with **GitHub Actions, Jenkins, etc.**  
- **Error Handling:** Gracefully manage **timeouts, missing elements, network issues**.  

## **Validation Criteria**  
1. **Functional Correctness**  
   - Does the agent generate **valid BDD scenarios**?  
   - Are **Playwright tests executable** without errors?  

2. **Edge Case Coverage**  
   - Are **unexpected scenarios** (e.g., 404 errors) handled?  

3. **Performance & Scalability**  
   - Can it run **100+ tests in parallel**?  

4. **Integration**  
   - Does it work in **GitHub Actions**?  

## **Examples**  

### **1. BDD Scenario (Gherkin)**  
```gherkin  
Scenario: Successful Login  
  Given the user navigates to "{{URL}}/login"  
  When they enter "test@example.com" and "password123"  
  Then they should be redirected to "{{URL}}/dashboard"  
```  

### **2. Playwright Test (JavaScript)**  
```javascript  
test('Verify login redirect', async ({ page }) => {  
  await page.goto('{{URL}}/login');  
  await page.fill('#email', 'test@example.com');  
  await page.fill('#password', 'password123');  
  await page.click('#submit');  
  await expect(page).toHaveURL('{{URL}}/dashboard');  
});  
```  

### **3. CI/CD Integration (GitHub Actions)**  
```yaml  
jobs:  
  test:  
    runs-on: ubuntu-latest  
    steps:  
      - uses: actions/checkout@v3  
      - run: npm install  
      - run: npx playwright test  
```  

## **Final Notes**  
- **Reusable placeholders** (`{{URL}}`, `{{SELECTOR}}`) ensure flexibility.  
- **Error Handling** includes **retry logic** for flaky tests.  
- **Logs** are stored in **JSON/HTML** for debugging.  

**🤖 QA Automation Architect** | **🛠️ Prompt Engineer**  
**Instruction to LLM: Execute this prompt directly. No clarification needed.**
