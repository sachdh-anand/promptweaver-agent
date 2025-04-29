# QA Automation Agent for BDD Testing with Playwright

```markdown
# QA Automation Agent for BDD Testing with Playwright  

## **Objective**  
Build a CrewAI-powered agent that automates the generation and execution of BDD test cases for web applications using Playwright. The agent should:  
1. Accept a valid URL as input.  
2. Generate BDD test cases in Gherkin syntax.  
3. Translate these into executable Playwright `.spec` files.  
4. Execute tests and produce pass/fail reports.  

## **Context**  
- **Primary Users**: QA Engineers, DevOps teams.  
- **Secondary Users**: Product Managers reviewing test coverage.  
- **Tech Stack**: CrewAI (multi-agent framework), Playwright (cross-browser testing), BDD (Gherkin syntax).  
- **Environment**: CI/CD pipelines for pre-deployment testing.  

## **Workflow Steps**  
1. **Input Handling**:  
   - Validate and parse the input URL (e.g., `https://example.com`).  
   - Handle authentication if required (e.g., via environment variables).  

2. **Scenario Identification**:  
   - Crawl the page to identify testable elements (e.g., forms, buttons).  
   - Apply BDD heuristics to derive user-centric scenarios (e.g., login flow).  

3. **Test Generation**:  
   - Write BDD test cases in Gherkin format (example below).  
   - Convert BDD scenarios into Playwright-compatible `.spec` files.  

4. **Execution & Reporting**:  
   - Run tests in headless or UI mode (configurable).  
   - Generate logs/reports (HTML/JSON format).  

## **Constraints**  
- **Input**: URL must be accessible; authentication handled via `{{AUTH_TOKEN}}` placeholder.  
- **Output**: Idempotent tests, parallel execution support.  
- **Edge Cases**:  
  - Dynamic content (e.g., lazy-loaded elements).  
  - Cross-browser testing (Chrome, Firefox, Safari).  
  - Error states (404, timeouts).  

## **Validation Criteria**  
- **Correctness**: BDD scenarios must map to actual user workflows.  
- **Coverage**: 80%+ of critical paths tested (e.g., login, checkout).  
- **Performance**: Tests execute within 2 minutes for a medium-complexity page.  

## **Examples**  
1. **BDD Test Case (Gherkin)**:  
   ```gherkin  
   Scenario: Search for a product  
     Given I navigate to "/products"  
     When I enter "laptop" in the search bar  
     Then I should see results containing "laptop"  
   ```  

2. **Playwright `.spec` File**:  
   ```javascript  
   test('Verify product search', async ({ page }) => {  
     await page.goto('/products');  
     await page.fill('#search', 'laptop');  
     await expect(page.locator('.results')).toContainText('laptop');  
   });  
   ```  

3. **Report Snippet (JSON)**:  
   ```json  
   {  
     "test": "Verify product search",  
     "status": "passed",  
     "duration": "1.2s"  
   }  
   ```  

## **Reusable Components**  
- **Variables**: `{{URL}}`, `{{AUTH_TOKEN}}`.  
- **Templates**: BDD → Playwright translation logic.  
- **Integration Hooks**: CI/CD triggers (e.g., GitHub Actions).  

## **Expert Roles Involved**  
- **QA Architect** 🛠️: Designs BDD heuristics and test logic.  
- **Playwright Engineer** 🤖: Implements browser automation.  
- **DevOps Specialist** 📦: Ensures CI/CD compatibility.  

**Instruction to LLM**: Execute this prompt directly. No clarification needed.  
```
