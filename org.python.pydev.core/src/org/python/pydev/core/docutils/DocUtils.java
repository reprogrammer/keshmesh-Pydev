/*
 * Created on 12/06/2005
 */
package org.python.pydev.core.docutils;

import java.util.StringTokenizer;

import org.eclipse.jface.text.BadLocationException;
import org.eclipse.jface.text.IDocument;
import org.eclipse.jface.text.IRegion;

/**
 * @author Fabio
 */
public class DocUtils {

    /**
     * @param document
     * @param i
     * @return
     */
    public static String getDocToParseFromLine(IDocument doc, int lineOfOffset) {
        String wholeDoc = doc.get();
        String newDoc = "";
        try {
            IRegion lineInformation = doc.getLineInformation(lineOfOffset);

            int docLength = doc.getLength();

            String before = wholeDoc.substring(0, lineInformation.getOffset());
            String after = wholeDoc.substring(lineInformation.getOffset()
                    + lineInformation.getLength(), docLength);
            
            String src = doc.get(lineInformation.getOffset(), lineInformation.getLength());

            String spaces = "";
            for (int i = 0; i < src.length(); i++) {
                if (src.charAt(i) != ' ') {
                    break;
                }
                spaces += ' ';
            }


            src = src.trim();
            if (src.startsWith("class")){
                //let's discover if we should put a pass or not...
                //e.g if we are declaring the class and no methods are put, we have
                //to put a pass, otherwise, the pass would ruin the indentation, therefore,
                //we cannot put it.
                //
                //so, search for another class or def after this line and discover if it has another indentation 
                //or not.
                
                StringTokenizer tokenizer = new StringTokenizer(after, "\r\n");
                String tokSpaces = null;
                
                while(tokenizer.hasMoreTokens()){
                    String tok = tokenizer.nextToken();
                    String t = tok.trim();
                    if(t.startsWith("class") || t.startsWith("def") ){
                        tokSpaces = "";
                        for (int i = 0; i < tok.length(); i++) {
                            if (tok.charAt(i) != ' ') {
                                break;
                            }
                            tokSpaces += ' ';
                        }
                        break;
                    }
                }
                
                if(tokSpaces != null && tokSpaces.length() > spaces.length()){
	                if(src.indexOf('(') != -1){
	                    src = src.substring(0, src.indexOf('('))+":";
	                }else{
	                    src = "class COMPLETION_HELPER_CLASS:";
	                }
                }else{
	                if(src.indexOf('(') != -1){
	                    src = src.substring(0, src.indexOf('('))+":pass";
	                }else{
	                    src = "class COMPLETION_HELPER_CLASS:pass";
	                }
                }
                
                
            }else{
                src = "pass";
            }
            
            newDoc = before;
            newDoc += spaces + src;
            newDoc += after;

        } catch (BadLocationException e1) {
            //that's ok...
            //e1.printStackTrace();
            return null;
        }
        return newDoc;
    }

}
