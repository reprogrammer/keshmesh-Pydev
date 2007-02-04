/*
 * Created on May 1, 2006
 */
package com.python.pydev.refactoring.wizards.rename;

import java.util.ArrayList;
import java.util.Iterator;
import java.util.List;

import org.eclipse.jface.util.Assert;
import org.eclipse.ltk.core.refactoring.RefactoringStatus;
import org.python.pydev.editor.codecompletion.revisited.modules.SourceModule;
import org.python.pydev.editor.codecompletion.revisited.visitors.Definition;
import org.python.pydev.editor.refactoring.RefactoringRequest;
import org.python.pydev.parser.jython.SimpleNode;
import org.python.pydev.parser.jython.ast.ClassDef;
import org.python.pydev.parser.jython.ast.FunctionDef;
import org.python.pydev.parser.jython.ast.NameTokType;
import org.python.pydev.parser.visitors.scope.ASTEntry;
import org.python.pydev.parser.visitors.scope.SequencialASTIteratorVisitor;

import com.python.pydev.analysis.messages.AbstractMessage;
import com.python.pydev.analysis.scopeanalysis.ScopeAnalysis;
import com.python.pydev.refactoring.refactorer.AstEntryRefactorerRequestConstants;
import com.python.pydev.refactoring.wizards.RefactorProcessFactory;

/**
 * This is the process that should take place when the definition maps to a class
 * definition (its AST is a ClassDef)
 * 
 * @see RefactorProcessFactory#getProcess(Definition) for details on choosing the 
 * appropriate process.
 * 
 * Note that the definition found may map to some module that is not actually
 * the current module, meaning that we may have a RenameClassProcess even
 * if the class definition is on some other module.
 * 
 * Important: the assumptions that can be made given this are:
 * - The current module has the token that maps to the definition found (so, it
 * doesn't need to be double checked)
 * - The module where the definition was found also does not need double checking
 * 
 * - All other modules need double checking if there is some other token in the 
 * workspace with the same name.
 * 
 * @author Fabio
 */
public class PyRenameClassProcess extends AbstractRenameWorkspaceRefactorProcess{

    /**
     * Do we want to debug?
     */
    public static final boolean DEBUG_CLASS_PROCESS = false;
    
    /**
     * Creates the rename class process with a definition.
     * 
     * @param definition a definition with a ClassDef.
     */
    public PyRenameClassProcess(Definition definition) {
        super(definition);
        Assert.isTrue(this.definition.ast instanceof ClassDef);
    }

    /**
     * When checking the class on a local scope, we have to cover the class definition
     * itself and any access to it (global)
     */
    protected void findReferencesToRenameOnLocalScope(RefactoringRequest request, RefactoringStatus status) {
        SimpleNode root = request.getAST();
        List<ASTEntry> oc = new ArrayList<ASTEntry>();
        
        oc.addAll(ScopeAnalysis.getCommentOcurrences(request.initialName, root));
        oc.addAll(ScopeAnalysis.getStringOcurrences(request.initialName, root));
        int currLine = request.ps.getCursorLine();
        int currCol = request.ps.getCursorColumn();
        int tokenLen = request.initialName.length();
        boolean foundAsComment = false;
        for(ASTEntry entry:oc){
            //it may be that we are actually hitting it in a comment and not in the class itself...
            //(for a comment it is ok just to check the line)
            int startLine = entry.node.beginLine-1;
            int startCol = entry.node.beginColumn-1;
            int endCol = entry.node.beginColumn+tokenLen-1;
            if(currLine == startLine && currCol >= startCol && currCol <= endCol){
                foundAsComment = true;
                break;
            }
        }

        ASTEntry classDefInAst = null;
        if(!foundAsComment && request.moduleName.equals(definition.module.getName())){
            classDefInAst = getOriginalClassDefInAst(root);
            
            if(classDefInAst == null){
                status.addFatalError("Unable to find the original definition for the class definition.");
                return;
            }
            
            while(classDefInAst.parent != null){
                if(classDefInAst.parent.node instanceof FunctionDef){
                    request.setAdditionalInfo(AstEntryRefactorerRequestConstants.FIND_REFERENCES_ONLY_IN_LOCAL_SCOPE, true); //it is in a local scope.
                    oc.addAll(this.getOccurrencesWithScopeAnalyzer(request));
                    addOccurrences(request, oc);
                    return;
                }
                classDefInAst = classDefInAst.parent;
            }

            //it is defined in the module we're looking for
            oc.addAll(this.getOccurrencesWithScopeAnalyzer(request));
        }else{
            //it is defined in some other module (or as a comment... so, we won't have an exact match)
            oc.addAll(ScopeAnalysis.getLocalOcurrences(request.initialName, root));
        }
        
        List<ASTEntry> attributeReferences = ScopeAnalysis.getAttributeReferences(request.initialName, root);
        
        if(classDefInAst != null){
            NameTokType funcName = ((ClassDef)classDefInAst.node).name;
            for (ASTEntry entry : attributeReferences) {
                if(entry.node != funcName){
                    oc.add(entry);
                }
            }
        }else{
            oc.addAll(attributeReferences);
        }

		addOccurrences(request, oc);
    }


    /**
     * @param simpleNode this is the module with the AST that has the function definition
     * @return the function definition that matches the original definition as an ASTEntry
     */
    private ASTEntry getOriginalClassDefInAst(SimpleNode simpleNode) {
        SequencialASTIteratorVisitor visitor = SequencialASTIteratorVisitor.create(simpleNode);
        Iterator<ASTEntry> it = visitor.getIterator(ClassDef.class);
        ASTEntry classDefEntry = null;
        while(it.hasNext()){
            classDefEntry = it.next();
            
            if(classDefEntry.node.beginLine == this.definition.ast.beginLine && 
                    classDefEntry.node.beginColumn == this.definition.ast.beginColumn){
                return classDefEntry;
            }
        }
        return null;
    }
    
    /**
     * This method is called for each module that may have some reference to the definition
     * we're looking for. 
     */
    protected List<ASTEntry> findReferencesOnOtherModule(RefactoringStatus status, String initialName, SourceModule module) {
        SimpleNode root = module.getAst();
        
        List<ASTEntry> entryOccurrences = ScopeAnalysis.getLocalOcurrences(initialName, root);
        entryOccurrences.addAll(ScopeAnalysis.getAttributeReferences(initialName, root));
        
        entryOccurrences.addAll(ScopeAnalysis.getCommentOcurrences(request.initialName, root));
        entryOccurrences.addAll(ScopeAnalysis.getStringOcurrences(request.initialName, root));
        return entryOccurrences;
    }
    
    @Override
    protected boolean getRecheckWhereDefinitionWasFound() {
        return true;
    }

}
