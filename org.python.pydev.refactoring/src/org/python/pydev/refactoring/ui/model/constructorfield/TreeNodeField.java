package org.python.pydev.refactoring.ui.model.constructorfield;

import org.python.pydev.refactoring.ast.adapters.SimpleAdapter;
import org.python.pydev.refactoring.ui.model.tree.ITreeNode;
import org.python.pydev.refactoring.ui.model.tree.TreeNodeSimple;

public class TreeNodeField extends TreeNodeSimple<SimpleAdapter> {

	public TreeNodeField(ITreeNode parent, SimpleAdapter adapter) {
		super(parent, adapter);
	}

	@Override
	public String getImageName() {
		return ITreeNode.NODE_ATTRIBUTE;
	}

}