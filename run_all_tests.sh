#!/bin/bash

echo "🧪 AI CAREER AGENT - COMPLETE TEST SUITE"
echo "========================================================"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test results
BACKEND_RESULT=0
FRONTEND_RESULT=0
CLI_RESULT=0
INTEGRATION_RESULT=0

echo -e "\n${BLUE}🔧 PHASE 1: BACKEND TESTING${NC}"
echo "----------------------------------------"
if python test_backend.py; then
    echo -e "${GREEN}✅ Backend tests PASSED${NC}"
    BACKEND_RESULT=1
else
    echo -e "${RED}❌ Backend tests FAILED${NC}"
fi

echo -e "\n${BLUE}🌐 PHASE 2: FRONTEND TESTING${NC}"
echo "----------------------------------------"
if ./test_frontend.sh; then
    echo -e "${GREEN}✅ Frontend tests PASSED${NC}"
    FRONTEND_RESULT=1
else
    echo -e "${RED}❌ Frontend tests FAILED${NC}"
fi

echo -e "\n${BLUE}🖥️ PHASE 3: CLI TESTING${NC}"
echo "----------------------------------------"
if python test_cli.py; then
    echo -e "${GREEN}✅ CLI tests PASSED${NC}"
    CLI_RESULT=1
else
    echo -e "${RED}❌ CLI tests FAILED${NC}"
fi

echo -e "\n${BLUE}🔗 PHASE 4: INTEGRATION TESTING${NC}"
echo "----------------------------------------"
if python test_integration.py; then
    echo -e "${GREEN}✅ Integration tests PASSED${NC}"
    INTEGRATION_RESULT=1
else
    echo -e "${RED}❌ Integration tests FAILED${NC}"
fi

# Calculate overall results
TOTAL_PASSED=$((BACKEND_RESULT + FRONTEND_RESULT + CLI_RESULT + INTEGRATION_RESULT))
TOTAL_TESTS=4

echo -e "\n========================================================"
echo -e "${BLUE}📊 FINAL TEST RESULTS${NC}"
echo "========================================================"
echo -e "Backend Tests:     $( [ $BACKEND_RESULT -eq 1 ] && echo -e "${GREEN}✅ PASSED" || echo -e "${RED}❌ FAILED" )${NC}"
echo -e "Frontend Tests:    $( [ $FRONTEND_RESULT -eq 1 ] && echo -e "${GREEN}✅ PASSED" || echo -e "${RED}❌ FAILED" )${NC}"
echo -e "CLI Tests:         $( [ $CLI_RESULT -eq 1 ] && echo -e "${GREEN}✅ PASSED" || echo -e "${RED}❌ FAILED" )${NC}"
echo -e "Integration Tests: $( [ $INTEGRATION_RESULT -eq 1 ] && echo -e "${GREEN}✅ PASSED" || echo -e "${RED}❌ FAILED" )${NC}"

echo ""
echo -e "Overall Score: ${BLUE}$TOTAL_PASSED/$TOTAL_TESTS${NC}"

if [ $TOTAL_PASSED -eq $TOTAL_TESTS ]; then
    echo -e "\n${GREEN}🎉 ALL TESTS PASSED! SYSTEM READY FOR PRODUCTION!${NC}"
    echo ""
    echo -e "${BLUE}🚀 Quick Start Commands:${NC}"
    echo "   python cli.py report                    # System health"
    echo "   python cli.py process-resume file.pdf   # Process resume" 
    echo "   python cli.py discover-jobs             # Find jobs"
    echo "   python cli.py run                       # Continuous mode"
    echo ""
    echo -e "${BLUE}🌐 Frontend:${NC}"
    echo "   cd frontend && npm run dev              # Start frontend"
    echo "   Visit: http://localhost:3000"
    echo ""
    echo -e "${BLUE}☁️ Deploy:${NC}"
    echo "   cd frontend && vercel --prod            # Deploy frontend"
    echo "   railway up                              # Deploy backend"
    
elif [ $TOTAL_PASSED -ge 3 ]; then
    echo -e "\n${YELLOW}✅ MOSTLY READY - Minor issues to address${NC}"
    echo "   🔧 Fix the failing component above"
    
else
    echo -e "\n${RED}⚠️ NEEDS WORK - Multiple issues found${NC}"
    echo "   🛠️ Address failing tests before deployment"
    exit 1
fi

echo -e "\n========================================================"