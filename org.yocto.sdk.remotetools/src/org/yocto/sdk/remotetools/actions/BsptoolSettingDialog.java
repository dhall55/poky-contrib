package org.yocto.sdk.remotetools.actions;

import org.eclipse.jface.dialogs.IDialogConstants;
import org.eclipse.jface.dialogs.IDialogSettings;
import org.eclipse.swt.SWT;
import org.eclipse.swt.events.ModifyEvent;
import org.eclipse.swt.events.ModifyListener;
import org.eclipse.swt.layout.GridData;
import org.eclipse.swt.layout.GridLayout;
import org.eclipse.swt.widgets.Button;
import org.eclipse.swt.widgets.Combo;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Control;
import org.eclipse.swt.widgets.Label;
import org.eclipse.swt.widgets.Shell;
import org.eclipse.swt.widgets.Text;
import org.yocto.sdk.remotetools.Activator;
import org.yocto.sdk.remotetools.Messages;
import org.yocto.sdk.remotetools.SWTFactory;

public class BsptoolSettingDialog extends BaseSettingDialog {
	
	static protected String TITLE="BspTool";
	
	protected boolean showPid=false;
	protected Float time;
	protected Button showPidButton;
	protected Text timeText;
	
	protected BsptoolSettingDialog(Shell parentShell, String title, String conn) {
		super(parentShell,title,conn);
	}
	
	public BsptoolSettingDialog(Shell parentShell) {
		this(parentShell,
				TITLE,
				Activator.getDefault().getDialogSettings().get(IBaseConstants.CONNECTION_NAME_BSPTOOL)
				);
	}
	
	public boolean getShowPid() {
		return showPid;
	}
	
	public Float getTime() {
		return time;
	}
	
	@Override
	protected Control createDialogArea(Composite parent) {
		Composite comp=(Composite)super.createDialogArea(parent);
		GridLayout topLayout = new GridLayout();
		comp.setLayout(topLayout);
		
		/*argument*/
		SWTFactory.createVerticalSpacer(comp, 1);
		createInternal(comp);
		
		updateOkButton();
		return comp;
	}
	
	protected void createInternal(Composite parent)
	{
		Composite projComp = new Composite(parent, SWT.NONE);
		GridLayout projLayout = new GridLayout();
		projLayout.numColumns = 4;
		projLayout.marginHeight = 0;
		projLayout.marginWidth = 0;
		projComp.setLayout(projLayout);
		GridData gd = new GridData(GridData.FILL_HORIZONTAL);
		projComp.setLayoutData(gd);
		
		Label label = new Label(projComp, SWT.NONE);
		label.setText ("karch");
		gd = new GridData();
		gd.horizontalSpan = 1;
		label.setLayoutData(gd);
		
		Combo combo = new Combo (projComp, SWT.NONE);
		combo.setItems (new String [] {"x86_64", "powerpc", "i386", "arm", "mips"});
		gd = new GridData(GridData.FILL_HORIZONTAL);
		gd.horizontalSpan = 2;
		combo.setLayoutData(gd);
			
		
	}

	@Override
	protected boolean updateOkButton() {
		boolean ret=super.updateOkButton();
		if(ret==true) {
			try {
				Float.valueOf(timeText.getText());
			}catch (Exception e) {
				Button button=getButton(IDialogConstants.OK_ID);
				if(button!=null)
					button.setEnabled(false);
				ret=false;
			}
		}
		return ret;
	}
	
	@Override
	protected void okPressed() {
		IDialogSettings settings = Activator.getDefault().getDialogSettings();
	    // store the value of the generate sections checkbox
		if(getCurrentConnection()==null) {
			settings.put(IBaseConstants.CONNECTION_NAME_BSPTOOL,
					(String)null);
		}else {
			settings.put(IBaseConstants.CONNECTION_NAME_BSPTOOL, 
					getCurrentConnection().getAliasName());
		}
		showPid=showPidButton.getSelection();
		time=new Float(timeText.getText());
		super.okPressed();
	}
}
