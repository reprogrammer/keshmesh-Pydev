/*
 * Created on Jan 15, 2006
 */
package org.python.pydev.ui;

import junit.framework.TestCase;

import org.eclipse.swt.widgets.Display;
import org.eclipse.swt.widgets.Shell;
import org.python.pydev.core.TestDependent;
import org.python.pydev.plugin.PydevPlugin;

public class SWTTest extends TestCase{

    protected Shell shell;
    protected Display display;
    private void createSShell() {
        shell = new org.eclipse.swt.widgets.Shell();
    }

    public void testIt(){
    	
    }
    
    /*
     * @see TestCase#setUp()
     */
    protected void setUp() throws Exception {
        super.setUp();
        PydevPlugin.setBundleInfo(new BundleInfoStub());
        try {
            if(TestDependent.HAS_SWT_ON_PATH){
                display = createDisplay();
                createSShell();
            }
        } catch (UnsatisfiedLinkError e) {
            //ok, ignore it.
            e.printStackTrace();
        }
    }

    /**
     * @return
     */
    protected Display createDisplay() {
        return new Display();
    }

    /*
     * @see TestCase#tearDown()
     */
    protected void tearDown() throws Exception {
        super.tearDown();
        PydevPlugin.setBundleInfo(null);
    }

    /**
     * @param display
     */
    protected void goToManual(Display display) {
        while (!shell.isDisposed()) {
            if (!display.readAndDispatch())
                display.sleep();
        }
        System.out.println("finishing...");
        display.dispose();
    }

}